/*
 * Copyright 2016-2019 by Heiko Schäfer <heiko@rangun.de>
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
#include <inttypes.h>
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
#include <glib/gprintf.h>

#include <libxml/tree.h>

#define FITEM_CMP(a, b) ((a)->fsize == (b)->fsize ? ((a)->fname == (b)->fname ? 0 : \
                         ((a)->fname < (b)->fname ? -1 : 1)) : ((a)->fsize < (b)->fsize ? -1 : 0))

#define FITEMLIST_CAST(x) ((FITEMLIST *const)(x))
#define REV_PARAMS_CAST(x) ((REV_PARAMS *)(x))
#define CAND_PARAMS_CAST(x) ((CAND_PARAMS *const)(x))

typedef struct {
    DISKFIT_FITEM *entries;
    size_t         size;
    guint64        total;
} FITEMLIST;

typedef struct {
    const gboolean stripdir;
    const guint64  tg;
    xmlNodePtr     root_node;
} DISP_PARAMS;

typedef struct {
    GTree         *const candidates;
    const mpz_ptr  fak_last;
    const mpz_ptr  fc;
    const mpz_ptr  aux;
    DISKFIT_FITEM *chunk;
    const size_t   nitems;
} CAND_PARAMS;

typedef struct {
    GSList               *rl;
    CAND_PARAMS          *cp;
    const mpz_ptr    rev_cur;
    const mpz_srcptr rev_tot;
} REV_PARAMS;

typedef struct {
    mpq_t aux_q, it_tot_q, fc_q;
    mpq_t nine, five;
    mpq_t ninehundred, ten;
} SCALE;

static volatile int _interrupted = 0;
static SCALE _scale;

static void term_handler(int sig, siginfo_t *si, void *unused) {

    (void) sig;
    (void) si;
    (void) unused;

    _interrupted = 1;
}

static inline void init_scale() {

    mpq_init(_scale.aux_q);
    mpq_init(_scale.it_tot_q);
    mpq_init(_scale.fc_q);

    mpq_init(_scale.nine);
    mpq_init(_scale.five);

    mpq_set_d(_scale.nine, 9.0);
    mpq_set_d(_scale.five, 5.0);

    mpq_init(_scale.ninehundred);
    mpq_init(_scale.ten);

    mpq_set_d(_scale.ninehundred, 900.0);
    mpq_set_d(_scale.ten, 10.0);
}

static inline void clear_scale() {

    mpq_clear(_scale.aux_q);
    mpq_clear(_scale.it_tot_q);
    mpq_clear(_scale.fc_q);

    mpq_clear(_scale.nine);
    mpq_clear(_scale.five);

    mpq_clear(_scale.ninehundred);
    mpq_clear(_scale.ten);
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

    register size_t i = 1u, jdec;

    for (; i < n; ++i) {

        const DISKFIT_FITEM h = { a[i].fname, a[i].fsize };
        register size_t j = i;

        while (j > 0u && a[(jdec = j - 1u)].fname > h.fname) {

            a[j].fname = a[jdec].fname;
            a[j].fsize = a[jdec].fsize;

            --j;
        }

        a[j].fname = h.fname;
        a[j].fsize = h.fsize;
    }
}

static inline gint cand_cmp(gconstpointer a, gconstpointer b) {

    if (FITEMLIST_CAST(a)->total > FITEMLIST_CAST(b)->total) {
        return -1;
    }

    if (FITEMLIST_CAST(a)->total < FITEMLIST_CAST(b)->total) {
        return 1;
    }

    if (FITEMLIST_CAST(a)->size < FITEMLIST_CAST(b)->size) {
        return 1;
    }

    if (FITEMLIST_CAST(a)->size > FITEMLIST_CAST(b)->size) {
        return -1;
    }

    return 0;
}

static inline gint include_cmp(gconstpointer a, gconstpointer b) {

    return (FITEMLIST_CAST(a)->size > FITEMLIST_CAST(b)->size ?
                            includes(FITEMLIST_CAST(a)->entries, FITEMLIST_CAST(a)->entries + FITEMLIST_CAST(a)->size,
                                     FITEMLIST_CAST(b)->entries, FITEMLIST_CAST(b)->entries + FITEMLIST_CAST(b)->size) :
                                     FALSE) ? 0 : cand_cmp(a, b);
}

static inline double scaleProgress(mpz_ptr aux, mpz_srcptr const it_tot) {

    mpq_set_z(_scale.aux_q, aux);
    mpq_set_z(_scale.it_tot_q, it_tot);

    mpq_div(_scale.fc_q, _scale.aux_q, _scale.it_tot_q);

    if (mpq_cmp_ui(_scale.fc_q, 50UL, 1UL) <= 0) {
        mpq_mul(_scale.aux_q, _scale.fc_q, _scale.nine);
        mpq_div(_scale.fc_q, _scale.aux_q, _scale.five);
    } else {
        mpq_add(_scale.aux_q, _scale.fc_q, _scale.ninehundred);
        mpq_div(_scale.fc_q, _scale.aux_q, _scale.ten);
    }

    return mpq_get_d(_scale.fc_q) + 0.5;
}

static void printProgress(mpz_ptr it_cur, mpz_srcptr const it_tot, void *user_data) {

    const gboolean initial = !mpz_cmp_ui(it_cur, 1UL);
    const unsigned long div = (mpz_cmp_ui(CAND_PARAMS_CAST(user_data)->fak_last, 90UL) < 0) ? 10000UL : 10UL;

    if (mpz_divisible_ui_p(it_cur, div) || initial) {

        mpz_mul_ui(CAND_PARAMS_CAST(user_data)->aux, it_cur, 100UL);
        mpz_set_d(CAND_PARAMS_CAST(user_data)->fc, scaleProgress(CAND_PARAMS_CAST(user_data)->aux, it_tot));

        if (mpz_cmp(CAND_PARAMS_CAST(user_data)->fc, CAND_PARAMS_CAST(user_data)->fak_last) || initial) {
            mpz_set(CAND_PARAMS_CAST(user_data)->fak_last, CAND_PARAMS_CAST(user_data)->fc);
            gmp_fprintf(stderr, "\033[sComputing for %zu files: %Zd%% ...\033[u",
                        CAND_PARAMS_CAST(user_data)->nitems, CAND_PARAMS_CAST(user_data)->fak_last);
        }
    }
}

static gboolean create_rev_list(gpointer key, gpointer value, gpointer data) {

    (void)value;

    mpz_add_ui(REV_PARAMS_CAST(data)->rev_cur, REV_PARAMS_CAST(data)->rev_cur, 1U);

    printProgress(REV_PARAMS_CAST(data)->rev_cur, REV_PARAMS_CAST(data)->rev_tot, REV_PARAMS_CAST(data)->cp);

    if (REV_PARAMS_CAST(data)->rl) {

        if (g_slist_find_custom(REV_PARAMS_CAST(data)->rl, FITEMLIST_CAST(key), include_cmp) == NULL) {
            REV_PARAMS_CAST(data)->rl = g_slist_prepend(REV_PARAMS_CAST(data)->rl, FITEMLIST_CAST(key));
        } else {
            g_free(FITEMLIST_CAST(key)->entries);
            g_slice_free(FITEMLIST, FITEMLIST_CAST(key));
        }

    } else {
        REV_PARAMS_CAST(data)->rl = g_slist_prepend(REV_PARAMS_CAST(data)->rl, FITEMLIST_CAST(key));
    }

    return _interrupted;
}

static void addCandidate(DISKFIT_FITEM *array, int len, guint64 total, void *user_data) {

    FITEMLIST *const l = g_slice_new(FITEMLIST);

    if (l) {

        CAND_PARAMS_CAST(user_data)->chunk = l->entries = CAND_PARAMS_CAST(user_data)->chunk != NULL ? CAND_PARAMS_CAST(user_data)->chunk :
                                 g_try_malloc_n(CAND_PARAMS_CAST(user_data)->nitems, sizeof(DISKFIT_FITEM));

        if (l->entries) {

            l->size  = len;
            l->total = total;

            memcpy(l->entries, array, l->size * sizeof(DISKFIT_FITEM));

            if (g_tree_lookup(CAND_PARAMS_CAST(user_data)->candidates, l) == NULL) {
                g_tree_insert(CAND_PARAMS_CAST(user_data)->candidates, l, l->entries);
                CAND_PARAMS_CAST(user_data)->chunk = NULL;
            } else {
                g_slice_free(FITEMLIST, l);
            }

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

static uint64_t blocksize(const char *grp, GKeyFile *rc) {

    if (rc && g_key_file_has_group(rc, grp) && g_key_file_has_key(rc, grp, "bs", NULL)) {
        return g_key_file_get_uint64(rc, grp, "bs", NULL);
    }

    return 0u;
}


static void print_copy() {
    g_fprintf(stderr, PACKAGE_STRING " - \u00a9 2016-2019 by Heiko Sch\u00e4fer <heiko@rangun.de>\n");
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

    size_t i;

    xmlNodePtr entry_node = NULL;

    g_qsort_with_data(FITEMLIST_CAST(key)->entries,
                        FITEMLIST_CAST(key)->size, sizeof(DISKFIT_FITEM),
                        fitem_ccmp, NULL);

    if(!p->root_node) {
        g_fprintf(stdout, "[ ");
    } else {
        entry_node = xmlNewNode(NULL, BAD_CAST "files");
    }

    for (i = 0; i < FITEMLIST_CAST(key)->size; ++i) {

        gchar *const bc = p->stripdir ?
        g_path_get_basename(FITEMLIST_CAST(key)->entries[i].fname) :
                        FITEMLIST_CAST(key)->entries[i].fname;

        if(!p->root_node) {
            g_fprintf(stdout, "'%s' ", bc);
        } else {
            xmlNodePtr file_node = xmlNewNode(NULL, BAD_CAST "filename");
            xmlAddChild(file_node, xmlNewText(BAD_CAST bc));
            xmlAddChild(entry_node, file_node);
        }

        if (p->stripdir) {
            g_free(bc);
        }
    }

    if(!p->root_node) {

        char hrs[1024];

        diskfit_hrsize(FITEMLIST_CAST(key)->total, hrs, 1023);
        g_fprintf(stdout, "]:%zu = %s (%.3f%%)\n",
            FITEMLIST_CAST(key)->size, hrs,
                (float)(FITEMLIST_CAST(key)->total * 100u) / (float)p->tg);
    } else {
        xmlAddChild(p->root_node, entry_node);
    }

    g_free(FITEMLIST_CAST(key)->entries);
    g_slice_free(FITEMLIST, FITEMLIST_CAST(key));
}

static void expandFilePattern(wordexp_t *const p, char *pat) {

    const int wr = wordexp(pat, p, WRDE_NOCMD | WRDE_APPEND);

    if (wr) {
        error(0, wr, "%s@%s:%d", __FUNCTION__, __FILE__, __LINE__);
    }
}

static void expandFilePatterns(wordexp_t *const p, int num, char **pats) {
    for (int i = 0; i < num; ++i) {
        expandFilePattern(p, pats[i]);
    }
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
        g_fprintf(stderr, "[DEBUG] targets read from %s\n", rcfile);
    } else {
        g_fprintf(stderr, "[DEBUG] no targets read\n");
    }

#endif

    if (argc < 2) {

        print_copy();

        g_fprintf(stdout, "\nUsage: %s [target_profile|target_size[G|M|K]] "
            "[file_pattern...|@pattern_file]\n\n", argv[0]);
        g_fprintf(stdout, "Omitting the file_pattern will just print the target size in Bytes.\n\n");
        g_fprintf(stdout, "Set environment variable DISKFIT_STRIPDIR to any value "
                "to strip directories from the output.\n");
        g_fprintf(stdout, "Set environment variable DISKFIT_XMLOUT to any value "
                "to get a compact XML-output.\n\nTarget profiles:\n");

        if (has_rc) {

            char hr_ptg[1024];
            char bsize[1024];
            gsize pi, plength;
            gchar **const profiles = g_key_file_get_groups(rc, &plength);

            for (pi = 0; pi < plength; ++pi) {
                *bsize = 0;
                diskfit_hrsize(diskfit_target_size(profiles[pi], tmap, rc), hr_ptg, 1023);
                const uint64_t bs = blocksize(profiles[pi], rc);
                if(bs) snprintf(bsize, 1023, "; block size = %" PRIu64 " byte%s", bs, bs > 1u ? "s" : "");
                g_fprintf(stdout, "\t%s = %s%s\n", profiles[pi], hr_ptg, bsize);
            }

            g_strfreev(profiles);

        } else {

            char hr_dvd[1024], hr_cd[1024];

            diskfit_hrsize(diskfit_target_size("dvd", NULL, NULL), hr_dvd, 1023);
            diskfit_hrsize(diskfit_target_size("cd", NULL, NULL), hr_cd, 1023);

            g_fprintf(stdout, "\tdvd = %s\n\tcd = %s\n", hr_dvd, hr_cd);
        }

        g_strfreev(env);
        g_free((void *)sd[1]);
        g_key_file_free(rc);
        g_free(rcfile);

        return EXIT_FAILURE;

    } else if (argc == 2) {

        g_fprintf(stdout, "%" G_GUINT64_FORMAT "\n", diskfit_target_size(argv[1], tmap,
                has_rc ? rc : NULL));

        g_strfreev(env);
        g_free((void *)sd[1]);
        g_key_file_free(rc);
        g_free(rcfile);

        return EXIT_SUCCESS;

    } else {

        size_t nitems = 0u;
        DISKFIT_FITEM *fitems = NULL;
        guint64 tsize = 0u;
        const uint64_t bs = has_rc ? blocksize(argc > 1 ? argv[1] : "dvd", rc) : 0u;
        const guint64  tg = diskfit_target_size(argc > 1 ? argv[1] : "dvd", tmap,
                                               has_rc ? rc : NULL);
        char hr_tot[1024], hr_tg[1024];
        wordexp_t p;

        print_copy();

        if(!tg) {
            g_fprintf(stderr, "invalid target or size given\n");
            return EXIT_FAILURE;
        }

        memset(&p, 0, sizeof(wordexp_t));

        if(*(argv[2]) == '@') {

            FILE *f = fopen(&(argv[2][1]), "r");

            if(f) {

                char cl[PATH_MAX - 2], *c;

                while(!feof(f)) {
                    if((c = fgets(cl, (PATH_MAX - 3) * sizeof(char), f))
                         && *c != '\n' && *c != 0) {

                        size_t len = strlen(cl);

                        if(len > 1) {

                            cl[len - 1] = 0;
                            char clq[PATH_MAX] = "\'";

                            strncat(clq, cl, PATH_MAX - 1);
                            strcat(clq, "\'");

                            expandFilePattern(&p, clq);
                        }
                    }
                }

                fclose(f);
            } else {
                g_fprintf(stderr, "Cannot open \'%s\': %s\n", &(argv[2][1]),
                    strerror(errno));
                return EXIT_FAILURE;
            }

        } else {
            expandFilePatterns(&p, argc - 2, &argv[2]);
        }

        int isInterrupted = 0;
        const gint64 mono_start = g_get_monotonic_time();

        if ((fitems = g_try_malloc_n(p.we_wordc, sizeof(DISKFIT_FITEM)))) {

            size_t j = 0u;

            for (; j < p.we_wordc; ++j) {

                struct stat st;

                if (!stat(p.we_wordv[j], &st)) {

                    if (S_ISREG(st.st_mode) && st.st_size) {

                        const uint64_t padded_size = st.st_size + (bs >
                            0u ? bs - (st.st_size & (bs - 1u)) : 0u);

                        if(padded_size <= tg) {

                            tsize += padded_size;

                            fitems[nitems].fname = p.we_wordv[j];
                            fitems[nitems].fsize = padded_size;

                            ++nitems;

                        } else {
                            diskfit_hrsize(padded_size, hr_tot, 1023);
                            g_fprintf(stderr, "[WARNING] File \'%s\' (%s) "
                            "is larger than target size - omitting\n",
                            p.we_wordv[j], hr_tot);
                        }
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

                mpz_init2(last_fac, 128);
                mpz_init2(fc, 128);
                mpz_init2(n, 128);

                CAND_PARAMS cp = { g_tree_new(cand_cmp), last_fac, fc, n, NULL, nitems };

                struct sigaction sa, sa_old;

                sa.sa_flags = SA_SIGINFO;
                sigemptyset(&sa.sa_mask);
                sa.sa_sigaction = term_handler;

                if (sigaction(SIGINT, &sa, &sa_old) == -1) {
                    error(0, errno, "%s@%s:%d", __FUNCTION__, __FILE__, __LINE__);
                }

                insertion_sort(fitems, nitems);

                init_scale();

                isInterrupted = diskfit_get_candidates(fitems, nitems, tsize, tg, addCandidate,
                                                       printProgress, &cp, &_interrupted);
                mpz_t rev_cur, rev_tot;
                const gint nodes = g_tree_nnodes(cp.candidates);

                mpz_init_set_ui(rev_tot, 2UL * nodes);
                mpz_init_set_ui(rev_cur, nodes);

                xmlDocPtr doc = NULL;
                xmlNodePtr root_node = NULL;
                const gboolean xml = g_environ_getenv(env, "DISKFIT_XMLOUT") != NULL;

                if(xml) {

                    doc = xmlNewDoc(BAD_CAST "1.0");
                    root_node = xmlNewNode(NULL, BAD_CAST "diskfit");

                    xmlDocSetRootElement(doc, root_node);
                }

                DISP_PARAMS dp = {
                    g_environ_getenv(env, "DISKFIT_STRIPDIR") != NULL,
                    tg, root_node
                };

                REV_PARAMS  rp = { NULL, &cp, rev_cur, rev_tot };

                g_tree_foreach(cp.candidates, create_rev_list, &rp);

                if (sigaction(SIGINT, &sa_old, NULL) == -1) {
                    error(0, errno, "%s@%s:%d", __FUNCTION__, __FILE__, __LINE__);
                }

                clear_scale();

                mpz_clear(n);
                mpz_clear(last_fac);
                mpz_clear(fc);
                mpz_clear(rev_cur);
                mpz_clear(rev_tot);

                if(xml) LIBXML_TEST_VERSION;

                g_slist_foreach(rp.rl, display_candidates, &dp);

                if(xml) {
                    xmlSaveFormatFileEnc("-", doc, "UTF-8", 1);
                    xmlFreeDoc(doc);
                    xmlCleanupParser();
                }

                g_slist_free(rp.rl);
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

        const gint64 mono_eta = (g_get_monotonic_time() - mono_start) / G_USEC_PER_SEC;
        const gint64 mono_h   = mono_eta / (gint64)3600;
        const gint64 mono_m   = (mono_eta - (mono_h * (gint64)3600)) / (gint64)60;
        const gint64 mono_s   = (mono_eta - (mono_h * (gint64)600) - (mono_m * (gint)60)) % (gint64)60;

        g_fprintf(stderr,
                "Total size: %s - Target size: %s - Total number of files: %zu - "
                "Time: %" G_GINT64_MODIFIER "d:%02" G_GINT64_MODIFIER "d:%02" G_GINT64_MODIFIER "d",
                hr_tot, hr_tg, nitems, mono_h, mono_m, mono_s);

        if (isInterrupted || _interrupted) {
            g_fprintf(stderr, " (interrupted)");
        }

        g_fprintf(stderr, "\n");
    }

    g_strfreev(env);
    g_free((void *)sd[1]);
    g_key_file_free(rc);
    g_free(rcfile);

    return EXIT_SUCCESS;
}

// kate: indent-mode cstyle; indent-width 4; replace-tabs on; remove-trailing-space on;
