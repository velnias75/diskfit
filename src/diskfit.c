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
    gboolean stripdir;
    guint64  tg;
} DISP_PARAMS;

typedef struct {
    GTree   *candidates;
    mpz_ptr  fak_last;
    mpz_ptr  fc;
    mpz_ptr  n;
    size_t   chunksize;
} CAND_PARAMS;

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

        DISKFIT_FITEM h = { a[i].fname, a[i].fsize };
        register size_t j = i;

        while (j > 0u && a[j - 1u].fname > h.fname) {
            memmove(&(a[j]), &(a[j - 1u]), sizeof(DISKFIT_FITEM));
            --j;
        }

        memmove(&(a[j]), &h, sizeof(DISKFIT_FITEM));
    }
}

static inline gint cand_cmp(gconstpointer a, gconstpointer b, gpointer user_data) {

    register const FITEMLIST *x = (FITEMLIST *)a, *y = (FITEMLIST *)b;
    (void)user_data;

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

    register const FITEMLIST *x = a, *y = b;

    const gint c = cand_cmp(x, y, NULL);

    if (c < 0) {

        register const FITEMLIST *min = x->size < y->size ? x : y;
        register const FITEMLIST *max = x->size < y->size ? y : x;

        return includes(max->entries, max->entries + max->size,
                        min->entries, min->entries + min->size) ? 0 : c;
    }

    return c;
}

static gboolean create_rev_list(gpointer key, gpointer value, gpointer data) {

    GSList   **l = (GSList **)data;
    FITEMLIST *k = key;

    (void)value;

    insertion_sort(k->entries, k->size);

    if (*l) {

        if (g_slist_find_custom(*l, k, include_cmp) == NULL) {
            *l = g_slist_prepend(*l, k);
        }

    } else {
        *l = g_slist_prepend(*l, k);
    }

    return FALSE;
}

static void addCandidate(DISKFIT_FITEM *array, int len, guint64 total,
                         mpz_ptr it_cur, mpz_srcptr const it_tot, void *user_data) {

    FITEMLIST    *l = g_malloc(sizeof(FITEMLIST));
    CAND_PARAMS *cp = user_data;

    if (l) {

        l->entries = g_malloc(cp->chunksize * sizeof(DISKFIT_FITEM));
        l->size  = len;
        l->total = total;

        if (l->entries) {

            mpz_mul_ui(cp->n, it_cur, 100UL);
            mpz_tdiv_q(cp->fc, cp->n, it_tot);

            if (mpz_cmp(cp->fc, cp->fak_last)) {
                mpz_set(cp->fak_last, cp->fc);
                gmp_fprintf(stderr, "\033[sCalculating: %Zd%% ...\033[u", cp->fak_last);
            }

            memmove(l->entries, array, sizeof(DISKFIT_FITEM) * len);
            g_tree_replace(cp->candidates, l, l->entries);

        } else {
            g_free(l);
        }
    }
}

static int tmap(const char *tgs, uint64_t *size, void *user_data) {

    GKeyFile *rc = user_data;

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
    return strcasecmp(((DISKFIT_FITEM *)a)->fname, ((DISKFIT_FITEM *)b)->fname);
}

static void display_candidates(gpointer key, gpointer data) {

    DISP_PARAMS *p = (DISP_PARAMS *)data;
    char hrs[1024];
    size_t i;

    fprintf(stdout, "[ ");

    g_qsort_with_data(((FITEMLIST *)key)->entries, ((FITEMLIST *)key)->size, sizeof(DISKFIT_FITEM),
                      fitem_ccmp, NULL);

    for (i = 0; i < ((FITEMLIST *)key)->size; ++i) {

        char *bc = p->stripdir ? g_path_get_basename(((FITEMLIST *)key)->entries[i].fname) :
                   ((FITEMLIST *)key)->entries[i].fname;

        fprintf(stdout, "'%s' ", bc);

        if (p->stripdir) {
            g_free(bc);
        }
    }

    diskfit_hrsize(((FITEMLIST *)key)->total, hrs, 1023);
    fprintf(stdout, "]:%zu = %s (%.3f%%)\n", ((FITEMLIST *)key)->size, hrs,
            (float)(((FITEMLIST *)key)->total * 100u) / (float)p->tg);
}

static inline void destroy_key(gpointer data) {
    g_free(((FITEMLIST *)data)->entries);
    g_free(data);
}

int main(int argc, char *argv[]) {

    GKeyFile *rc = g_key_file_new();
    gchar **env = g_get_environ();
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
            gchar **profiles = g_key_file_get_groups(rc, &plength);

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

        if ((fitems = g_malloc(p.we_wordc * sizeof(DISKFIT_FITEM)))) {

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

                    DISKFIT_FITEM *f = g_realloc(fitems, nitems * sizeof(DISKFIT_FITEM));

                    if (f && f != fitems) {
                        fitems = f;
                    }
                }

                fprintf(stderr, "\033[sCalculating: 0%% ...\033[u");

                mpz_t last_fac, fc, n;

                mpz_init(last_fac);
                mpz_init(fc);
                mpz_init(n);

                CAND_PARAMS cp = { g_tree_new_full(cand_cmp, NULL, destroy_key, NULL),
                                   last_fac, fc, n, nitems
                                 };

                diskfit_get_candidates(fitems, nitems, tsize, tg, addCandidate, &cp);

                mpz_clear(last_fac);
                mpz_clear(fc);
                mpz_clear(n);

                DISP_PARAMS dp = { g_environ_getenv(env, "DISKFIT_STRIPDIR") != NULL, tg };

                GSList *rl = NULL;

                g_tree_foreach(cp.candidates, create_rev_list, &rl);
                g_slist_foreach(rl, display_candidates, &dp);

                g_slist_free(rl);
                g_tree_destroy(cp.candidates);
            }

            g_free(fitems);

        } else {
            error(0, ENOMEM, "%s@%s:%d", __FUNCTION__, __FILE__, __LINE__);
        }

        wordfree(&p);

        diskfit_hrsize(tsize, hr_tot, 1023);
        diskfit_hrsize(tg, hr_tg, 1023);
        fprintf(stderr, "Total size: %s - Target size: %s - Total number of files: %zu\n", hr_tot,
                hr_tg, nitems);
    }

    g_strfreev(env);
    g_free((void *)sd[1]);
    g_key_file_free(rc);
    g_free(rcfile);

    return EXIT_SUCCESS;
}

// kate: indent-mode cstyle; indent-width 4; replace-tabs on; 
