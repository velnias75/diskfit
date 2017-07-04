/*
 * Copyright 2016-2017 by Heiko Schäfer <heiko@rangun.de>
 *
 * This file is part of DiskFit.
 *
 * DiskFit is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 3 of
 * the License, or (at your option) any later version.
 *
 * DiskFit is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with DiskFit.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <error.h>
#include <errno.h>
#include <sys/stat.h>
#include <unistd.h>
#include <signal.h>

#include <wordexp.h>
#include <libgen.h>

#include "diskfit.h"
#include "fitem.h"

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <glib.h>

#define FITEM_CMP(a, b) ((a)->fsize == (b)->fsize ? ((a)->fname == (b)->fname ? 0 : \
                         ((a)->fname < (b)->fname ? -1 : 1)) : ((a)->fsize < (b)->fsize ? -1 : 0))

typedef struct {
    DISKFIT_FITEM *entries;
    size_t         size;
    guint64        total;
} FITEMLIST;

typedef struct {
    const gboolean stripdir;
    const guint64  tg;
} DISP_PARAMS;

typedef struct {
    GTree         *const candidates;
    const mpz_ptr  fak_last;
    const mpz_ptr  fc;
    const mpz_ptr  aux;
    DISKFIT_FITEM *chunk;
    const size_t   nitems;
    const gint64   mono_start;
    const mpf_ptr  mono_itert;
    const mpf_ptr  it_cur_f;
    const mpf_ptr  it_eta_f;
    gboolean       first_it;
    double         it_tot_d;
} CAND_PARAMS;

static volatile int _interrupted = 0;

static void term_handler(int sig, siginfo_t *si, void *unused) {

    (void) sig;
    (void) si;
    (void) unused;

    _interrupted = 1;
}

static inline gboolean includes(const DISKFIT_FITEM *first1, const DISKFIT_FITEM *last1,
                                const DISKFIT_FITEM *first2, const DISKFIT_FITEM *last2) {

    for (; first2 != last2; ++first1) {

        if (first1 == last1 || first2->fname < first1->fname) {
            return FALSE;
        }

        if (!(first1->fname < first2->fname)) {
            ++first2;
        }
    }

    return TRUE;
}

static inline void insertion_sort(DISKFIT_FITEM *a, size_t n) {

    register size_t i = 1u;

    for (; i < n; ++i) {

        const DISKFIT_FITEM h = { a[i].fname, a[i].fsize };
        register size_t j = i;

        while (j > 0u && a[j - 1u].fname > h.fname) {

            a[j].fname = a[j - 1u].fname;
            a[j].fsize = a[j - 1u].fsize;

            --j;
        }

        a[j].fname = h.fname;
        a[j].fsize = h.fsize;
    }
}

static inline gint cand_cmp(gconstpointer a, gconstpointer b) {

    register const FITEMLIST *x = (FITEMLIST *)a;
    register const FITEMLIST *y = (FITEMLIST *)b;

    if (x->total < y->total) {
        return 1;
    }

    if (x->total > y->total) {
        return -1;
    }

    if (x->size < y->size) {
        return 1;
    }

    if (x->size > y->size) {
        return -1;
    }

    return 0;
}

static gint include_cmp(gconstpointer a, gconstpointer b) {

    const gint c = cand_cmp(a, b);

    if (c < 0) {

        register const FITEMLIST *x = a, *y = b;
        register const FITEMLIST *min = x->size < y->size ? x : y;
        register const FITEMLIST *max = x->size < y->size ? y : x;

        return includes(max->entries, max->entries + max->size,
                        min->entries, min->entries + min->size) ? 0 : c;
    }

    return c;
}

static gboolean create_rev_list(gpointer key, gpointer value, gpointer data) {

    GSList    **const l = (GSList **)data;
    FITEMLIST *const  k = key;

    (void)value;

    insertion_sort(k->entries, k->size);

    if (*l) {

        if (g_slist_find_custom(*l, k, include_cmp) == NULL) {
            *l = g_slist_prepend(*l, k);
        } else {
            g_free(k->entries);
            g_slice_free(FITEMLIST, k);
        }

    } else {
        *l = g_slist_prepend(*l, k);
    }

    return FALSE;
}

static void addCandidate(DISKFIT_FITEM *array, int len, guint64 total,
                         mpz_ptr it_cur, mpz_srcptr const it_tot, void *user_data) {

    FITEMLIST *const l = g_slice_new(FITEMLIST);

    if (l) {

        CAND_PARAMS *const cp = user_data;

        cp->chunk = l->entries = cp->chunk != NULL ? cp->chunk :
                                 g_try_malloc_n(cp->nitems, sizeof(DISKFIT_FITEM));

        if (l->entries) {

            if (cp->nitems < 20) {
                mpz_set_d(cp->fc, (mpz_get_d(it_cur) * 100u) / (cp->it_tot_d != 0.0 ? cp->it_tot_d :
                          (cp->it_tot_d = mpz_get_d(it_tot))));
            } else {
                mpz_mul_ui(cp->aux, it_cur, 100UL);
                mpz_tdiv_q(cp->fc, cp->aux, it_tot);
            }

            if (cp->first_it || mpz_cmp(cp->fc, cp->fak_last)) {

                cp->first_it = FALSE;

                mpz_set(cp->fak_last, cp->fc);
                mpz_sub(cp->aux, it_tot, it_cur);
                mpf_set_z(cp->it_eta_f, cp->aux);
                mpf_set_z(cp->it_cur_f, it_cur);
                mpf_set_ui(cp->mono_itert, g_get_monotonic_time() - cp->mono_start);
                mpf_div(cp->mono_itert, cp->mono_itert, cp->it_cur_f);
                mpf_mul(cp->mono_itert, cp->mono_itert, cp->it_eta_f);
                mpf_div_ui(cp->mono_itert, cp->mono_itert, G_USEC_PER_SEC);

                GDateTime *const d1 = g_date_time_new_now_local();
                GDateTime *const d2 = d1 ? g_date_time_add_seconds(d1, mpf_get_d(cp->mono_itert)) :
                                      NULL;
                gchar     *const s0 =
                    d2 ? g_date_time_format(
                        d2, "\033[sComputing for %%zu files: %%Zd%%%% ... ETA: %X\033[u") :
                    "\033[sComputing for %zu files: %Zd%% ...\033[u";

                gmp_fprintf(stderr, s0, cp->nitems, cp->fak_last);

                if (d1) {

                    g_date_time_unref(d1);

                    if (d2) {
                        g_date_time_unref(d2);
                        g_free(s0);
                    }
                }
            }

            l->size  = len;
            l->total = total;

            DISKFIT_FITEM *le_beg = l->entries, *ar_beg = array;
            DISKFIT_FITEM *const le_end = l->entries + len;

            while (le_beg < le_end) {

                le_beg->fname = ar_beg->fname;
                le_beg->fsize = ar_beg->fsize;

                ++le_beg;
                ++ar_beg;
            }

            //if (g_tree_lookup(cp->candidates, l) == NULL) {
                g_tree_insert(cp->candidates, l, l->entries);
                cp->chunk = NULL;
            /*} else {
                g_slice_free(FITEMLIST, l);
            } */

        } else {
            g_slice_free(FITEMLIST, l);
        }
    }
}

static int tmap(const char *tgs, uint64_t *size, void *user_data) {

    GKeyFile *const rc = user_data;

    if (rc && g_key_file_has_group(rc, tgs) && g_key_file_has_key(rc, tgs, "size", NULL)) {
        *size = g_key_file_get_uint64(rc, tgs, "size", NULL);
        return 1;
    }

    return 0;
}

static void print_copy() {
    fprintf(stderr, PACKAGE_STRING " - \u00a9 2016-2017 by Heiko Sch\u00e4fer <heiko@rangun.de>\n");
}

static inline gint fitem_ccmp(gconstpointer a, gconstpointer b, gpointer d) {

    (void)d;

    gchar *a_utf_cf = g_utf8_casefold(((DISKFIT_FITEM *)a)->fname, -1);
    gchar *b_utf_cf = g_utf8_casefold(((DISKFIT_FITEM *)b)->fname, -1);

    const gint r = g_strcmp0(a_utf_cf, b_utf_cf);

    g_free(a_utf_cf);
    g_free(b_utf_cf);

    return r;
}

static void display_candidates(gpointer key, gpointer data) {

    const DISP_PARAMS *const p = (DISP_PARAMS *)data;
    FITEMLIST *const l = (FITEMLIST *)key;

    char hrs[1024];
    size_t i;

    fprintf(stdout, "[ ");

    g_qsort_with_data(l->entries, l->size, sizeof(DISKFIT_FITEM), fitem_ccmp, NULL);

    for (i = 0; i < l->size; ++i) {

        char *const bc = p->stripdir ? g_path_get_basename(l->entries[i].fname) :
                         l->entries[i].fname;

        fprintf(stdout, "'%s' ", bc);

        if (p->stripdir) {
            g_free(bc);
        }
    }

    diskfit_hrsize(l->total, hrs, 1023);
    fprintf(stdout, "]:%zu = %s (%.3f%%)\n", l->size, hrs,
            (float)(l->total * 100u) / (float)p->tg);

    g_free(l->entries);
    g_slice_free(FITEMLIST, l);
}

int main(int argc, char *argv[]) {

    GKeyFile *const rc = g_key_file_new();
    gchar **const env = g_get_environ();
    gchar *rcfile = NULL;

    const gchar *sd[] = {
        "./",
        g_strconcat(g_environ_getenv(env, "HOME"), "/", NULL),
        SYSCONFDIR,
        NULL
    };

    const gboolean has_rc = g_key_file_load_from_dirs(rc, ".diskfitrc", sd, &rcfile,
                            G_KEY_FILE_NONE, NULL) || g_key_file_load_from_dirs(rc, "diskfitrc",
                                    sd, &rcfile, G_KEY_FILE_NONE, NULL);

    diskfit_set_mem_funcs(g_try_malloc, g_free);

#ifndef NDEBUG

    if (has_rc) {
        fprintf(stderr, "[DEBUG] targets read from %s\n", rcfile);
    } else {
        fprintf(stderr, "[DEBUG] no targets read\n");
    }

#endif

    if (argc < 2) {

        print_copy();

        fprintf(stdout, "\nUsage: %s [target_profile|target_size[G|M|K]] [file_pattern...]\n\n",
                argv[0]);
        fprintf(stdout, "Omitting the file_pattern will just print the target size in Bytes.\n\n");
        fprintf(stdout, "Set environment variable DISKFIT_STRIPDIR to any value "
                "to strip directories from the output.\n\nTarget profiles:\n");

        if (has_rc) {

            char hr_ptg[1024];
            gsize pi, plength;
            gchar **const profiles = g_key_file_get_groups(rc, &plength);

            for (pi = 0; pi < plength; ++pi) {
                diskfit_hrsize(diskfit_target_size(profiles[pi], tmap, rc), hr_ptg, 1023);
                fprintf(stdout, "\t%s = %s\n", profiles[pi], hr_ptg);
            }

            g_strfreev(profiles);

        } else {

            char hr_dvd[1024], hr_cd[1024];

            diskfit_hrsize(diskfit_target_size("dvd", NULL, NULL), hr_dvd, 1023);
            diskfit_hrsize(diskfit_target_size("cd", NULL, NULL), hr_cd, 1023);

            fprintf(stdout, "\tdvd = %s\n\tcd = %s\n", hr_dvd, hr_cd);
        }

        g_strfreev(env);
        g_free((void *)sd[1]);
        g_key_file_free(rc);
        g_free(rcfile);

        return EXIT_FAILURE;

    } else if (argc == 2) {

        fprintf(stdout, "%" G_GUINT64_FORMAT "\n", diskfit_target_size(argv[1], tmap,
                has_rc ? rc : NULL));

        g_strfreev(env);
        g_free((void *)sd[1]);
        g_key_file_free(rc);
        g_free(rcfile);

        return EXIT_SUCCESS;

    } else {

        int i;
        size_t nitems = 0u;
        DISKFIT_FITEM *fitems = NULL;
        guint64 tsize = 0u;
        const guint64 tg = diskfit_target_size(argc > 1 ? argv[1] : "dvd", tmap,
                                               has_rc ? rc : NULL);
        char hr_tot[1024], hr_tg[1024];
        wordexp_t p;

        print_copy();

        memset(&p, 0, sizeof(wordexp_t));

        for (i = 0; i < argc - 2; ++i) {

            const int wr = wordexp(argv[i + 2], &p, WRDE_NOCMD | WRDE_APPEND);

            if (wr) {
                error(0, wr, "%s@%s:%d", __FUNCTION__, __FILE__, __LINE__);
            }
        }

        int isInterrupted = 0;
        const gint64 mono_start = g_get_monotonic_time();

        if ((fitems = g_try_malloc_n(p.we_wordc, sizeof(DISKFIT_FITEM)))) {

            size_t j = 0u;

            for (; j < p.we_wordc; ++j) {

                struct stat st;

                if (!stat(p.we_wordv[j], &st)) {

                    if (S_ISREG(st.st_mode)) {

                        tsize += st.st_size;

                        fitems[nitems].fname = p.we_wordv[j];
                        fitems[nitems].fsize = st.st_size;

                        ++nitems;
                    }

                } else {
                    error(0, errno, "%s@%s:%d: %s", __FUNCTION__, __FILE__, __LINE__,
                          p.we_wordv[j]);
                }
            }

            if (nitems > 0) {

                if (nitems < p.we_wordc) {

                    DISKFIT_FITEM *const f = g_try_realloc_n(fitems, nitems, sizeof(DISKFIT_FITEM));

                    if (f && f != fitems) {
                        fitems = f;
                    }
                }

                mpz_t last_fac, fc, n;
                mpf_t mono_itert, it_cur_f, it_eta_f;

                mpz_init2(last_fac, 128);
                mpz_init2(fc, 128);
                mpz_init2(n, 128);
                mpf_init(mono_itert);
                mpf_init(it_cur_f);
                mpf_init(it_eta_f);

                CAND_PARAMS cp = { g_tree_new(cand_cmp), last_fac, fc, n, NULL, nitems,
                                   g_get_monotonic_time(), mono_itert, it_cur_f, it_eta_f,
                                   TRUE, 0.0
                                 };

                struct sigaction sa, sa_old;

                sa.sa_flags = SA_SIGINFO;
                sigemptyset(&sa.sa_mask);
                sa.sa_sigaction = term_handler;

                if (sigaction(SIGINT, &sa, &sa_old) == -1) {
                    error(0, errno, "%s@%s:%d", __FUNCTION__, __FILE__, __LINE__);
                }

                isInterrupted = diskfit_get_candidates(fitems, nitems, tsize, tg, addCandidate,
                                                       &cp, &_interrupted);

                if (sigaction(SIGINT, &sa_old, NULL) == -1) {
                    error(0, errno, "%s@%s:%d", __FUNCTION__, __FILE__, __LINE__);
                }

                mpz_clear(last_fac);
                mpz_clear(fc);
                mpz_clear(n);
                mpf_clear(mono_itert);
                mpf_clear(it_cur_f);
                mpf_clear(it_eta_f);

                DISP_PARAMS dp = { g_environ_getenv(env, "DISKFIT_STRIPDIR") != NULL, tg };

                GSList *rl = NULL;

                g_tree_foreach(cp.candidates, create_rev_list, &rl);
                g_slist_foreach(rl, display_candidates, &dp);

                g_slist_free(rl);
                g_tree_destroy(cp.candidates);

                g_free(cp.chunk);
            }

            g_free(fitems);

        } else {
            error(0, ENOMEM, "%s@%s:%d", __FUNCTION__, __FILE__, __LINE__);
        }

        wordfree(&p);

        diskfit_hrsize(tsize, hr_tot, 1023);
        diskfit_hrsize(tg, hr_tg, 1023);

        const long mono_eta = (g_get_monotonic_time() - mono_start) / G_USEC_PER_SEC;

        fprintf(stderr,
                "Total size: %s - Target size: %s - Total number of files: %zu - "
                "Time: %ld:%02ld:%02ld", hr_tot, hr_tg, nitems,
                mono_eta / 3600L, mono_eta / 60L, mono_eta % 60L);

        if (isInterrupted) {
            fprintf(stderr, " (interrupted)");
        }

        fprintf(stderr, "\n");
    }

    g_strfreev(env);
    g_free((void *)sd[1]);
    g_key_file_free(rc);
    g_free(rcfile);

    return EXIT_SUCCESS;
}

// kate: indent-mode cstyle; indent-width 4; replace-tabs on;
