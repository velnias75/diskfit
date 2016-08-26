/*
 * Copyright 2016 by Heiko Schäfer <heiko@rangun.de>
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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <glib.h>

#define FITEM_CMP(a, b) ((a)->fsize == (b)->fsize ? ((a)->fname == (b)->fname ? 0 : \
                         ((a)->fname < (b)->fname ? -1 : 1)) : ((a)->fsize < (b)->fsize ? -1 : 0))

typedef struct {
    FITEM *entries;
    size_t size;
    guint64 total;
} FITEMLIST;

typedef struct {
    gboolean stripdir;
    guint64 tg;
} DISP_PARAMS;

typedef struct {
    GTree *candidates;
    unsigned long fak_last;
    FITEM *chunk;
    size_t chunksize;
} CAND_PARAMS;

static inline gboolean includes(const FITEM *first1, const FITEM *last1,
                                const FITEM *first2, const FITEM *last2) {

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

static inline void insertion_sort(FITEM *a, size_t n) {

    register size_t i = 1u;

    for (; i < n; ++i) {

        FITEM h = { a[i].fname, a[i].fsize };
        register size_t j = i;

        while (j > 0u && a[j - 1u].fname > h.fname) {
            memmove(&(a[j]), &(a[j - 1u]), sizeof(FITEM));
            --j;
        }

        memmove(&(a[j]), &h, sizeof(FITEM));
    }
}

static inline gint cand_cmp(gconstpointer a, gconstpointer b) {

    register const FITEMLIST *x = (FITEMLIST *)a, *y = (FITEMLIST *)b;

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

    const gint c = cand_cmp(x, y);

    if (c < 0) {

        register const FITEMLIST *min = x->size < y->size ? x : y;
        register const FITEMLIST *max = x->size < y->size ? y : x;

        return includes(max->entries, max->entries + max->size,
                        min->entries, min->entries + min->size) ? 0 : c;
    }

    return c;
}

static gboolean create_rev_list(gpointer key, gpointer value, gpointer data) {

    GSList **l = (GSList **)data;
    FITEMLIST *k = key;

    (void)value;

    insertion_sort(k->entries, k->size);

    if (*l) {

        if (g_slist_find_custom(*l, k, include_cmp) == NULL) {
            *l = g_slist_prepend(*l, k);
        } else {
            g_free(k->entries);
            g_free(k);
        }

    } else {
        *l = g_slist_prepend(*l, k);
    }

    return FALSE;
}

static void addCandidate(FITEM *array, int len, guint64 total,
                         const unsigned long it_cur, const unsigned long it_tot, void *user_data) {

    FITEMLIST    *l = g_malloc(sizeof(FITEMLIST));
    CAND_PARAMS *cp = user_data;

    if (l) {

        cp->chunk = l->entries = cp->chunk != NULL ? cp->chunk :
                                 g_malloc(cp->chunksize * sizeof(FITEM));
        l->size = len;
        l->total = total;

        if (l->entries) {

            const unsigned long fc = (it_cur * 100u) / it_tot;

            if (fc != cp->fak_last) {
                fprintf(stderr, "\033[sCalculating: %lu%% ...\033[u", (cp->fak_last = fc));
            }

            memmove(l->entries, array, sizeof(FITEM) * len);

            if (g_tree_lookup(cp->candidates, l) == NULL) {
                g_tree_insert(cp->candidates, l, l->entries);
                cp->chunk = NULL;
            } else {
                g_free(l);
            }

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
    fprintf(stderr, PACKAGE_STRING " - \u00a9 2016 by Heiko Sch\u00e4fer <heiko@rangun.de>\n");
}

static inline gint fitem_ccmp(gconstpointer a, gconstpointer b, gpointer d) {
    (void)d;
    return strcasecmp(((FITEM *)a)->fname, ((FITEM *)b)->fname);
}

static void display_candidates(gpointer key, gpointer data) {

    DISP_PARAMS *p = (DISP_PARAMS *)data;
    char hrs[1024];
    size_t i;

    fprintf(stdout, "[ ");

    g_qsort_with_data(((FITEMLIST *)key)->entries, ((FITEMLIST *)key)->size, sizeof(FITEM),
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
    fprintf(stdout, "] = %s (%.3f%%)\n", hrs,
            (float)(((FITEMLIST *)key)->total * 100u) / (float)p->tg);

    g_free(((FITEMLIST *)key)->entries);
    g_free(key);
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

        fprintf(stdout, "\nUsage: %s [target_profile|target_size[G|M|K]] [file_pattern...]\n\n", argv[0]);
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
        size_t j, nitems = 0;
        FITEM *fitems = NULL;
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

        if ((fitems = g_malloc(p.we_wordc * sizeof(FITEM)))) {

            for (j = 0; j < p.we_wordc; ++j) {

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

                    FITEM *f = g_realloc(fitems, nitems * sizeof(FITEM));

                    if (f && f != fitems) {
                        fitems = f;
                    }
                }

                fprintf(stderr, "\033[sCalculating: 0%% ...\033[u");

                CAND_PARAMS cp = { g_tree_new(cand_cmp), 0u, NULL, nitems };

                diskfit_get_candidates(fitems, nitems, tsize, tg, addCandidate, &cp);

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
        fprintf(stderr, "Total size: %s - Target size: %s\n", hr_tot, hr_tg);
    }

    g_strfreev(env);
    g_free((void *)sd[1]);
    g_key_file_free(rc);
    g_free(rcfile);

    return EXIT_SUCCESS;
}

// kate: indent-mode cstyle; indent-width 4; replace-tabs on; 
