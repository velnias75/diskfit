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

typedef struct {
    FITEM *entries;
    size_t size;
    guint64 total;
} FITEMLIST;

typedef struct {
    gboolean stripdir;
    guint64 tg;
} DISP_PARAMS;

static GTree *CANDIDATES = NULL;
static unsigned long FAK_LST = 0u;

inline static int fitem_cmp(const void *a, const void *b) {
    return a == b ? 0 : (a < b ? -1 : 1);
}

inline static gint cand_cmp(gconstpointer a, gconstpointer b) {

    if (((FITEMLIST *) a)->total < ((FITEMLIST *) b)->total) {
        return -1;
    }

    if (((FITEMLIST *) a)->total > ((FITEMLIST *) b)->total) {
        return 1;
    }

    return 0;
}

inline static gint eq(gconstpointer a, gconstpointer b) {

    const FITEMLIST *x = (FITEMLIST *)a, *y = (FITEMLIST *)b;

    if (x->size == y->size && x->total == y->total) {

        size_t i;
        const size_t min = (x->size < y->size ? x->size : y->size) - 1u;
        gboolean dup = FALSE;

        for (i = 0; !(dup |= x->entries[i].fname == y->entries[i].fname) && i < min; ++i);

        return dup ? 0 : cand_cmp(a, b);
    }

    return cand_cmp(a, b);
}

static void addCandidate(FITEM *array, int len, guint64 total,
                         const unsigned long it_cur, const unsigned long it_tot) {

    FITEMLIST *l = g_malloc(sizeof(FITEMLIST));

    if (l) {

        l->entries = g_malloc(len * sizeof(FITEM));
        l->size = len;
        l->total = total;

        if (l->entries) {

            const unsigned long fc = (it_cur * 100u) / it_tot;

            if (fc != FAK_LST) {
                fprintf(stderr, "\033[sCalculating: %lu%% ...\033[u", (FAK_LST = fc));
            }

            memmove(l->entries, array, sizeof(FITEM) * len);
            qsort(l->entries, l->size, sizeof(FITEM), fitem_cmp);

            if (g_tree_lookup(CANDIDATES, l) == NULL) {
                g_tree_insert(CANDIDATES, l, l->entries);
            } else {
                g_free(l->entries);
                g_free(l);
            }

        } else {
            g_free(l);
        }
    }
}

static void print_copy() {
    fprintf(stderr, PACKAGE_STRING " - (c) 2016 by Heiko Sch\u00e4fer <heiko@rangun.de>\n");
}

inline static int fitem_ccmp(const void *a, const void *b) {
    return strcasecmp(((FITEM *)a)->fname, ((FITEM *)b)->fname);
}

static gboolean display_candidates(gpointer key, gpointer value, gpointer data) {

    DISP_PARAMS *p = (DISP_PARAMS *)data;
    char hrs[1024];
    size_t i;

    fprintf(stdout, "[ ");

    qsort(((FITEMLIST *)key)->entries, ((FITEMLIST *)key)->size, sizeof(FITEM), fitem_ccmp);

    for (i = 0; i < ((FITEMLIST *)key)->size; ++i) {

        char *bc = p->stripdir ? g_strdup(((FITEMLIST *)key)->entries[i].fname) :
                   ((FITEMLIST *)key)->entries[i].fname;

        fprintf(stdout, "'%s' ", p->stripdir ? basename(bc) : bc);

        if (p->stripdir) {
            g_free(bc);
        }
    }

    diskfit_hrsize(((FITEMLIST *)key)->total, hrs, 1023);
    fprintf(stdout, "] = %s (%.3f%%)\n", hrs,
            (float)(((FITEMLIST *)key)->total * 100u) / (float)p->tg);

    g_free(value);
    g_free(key);

    return FALSE;
}

int main(int argc, char *argv[]) {

    if (argc < 2) {

        print_copy();

        fprintf(stdout, "\nUsage: %s (cd|dvd|target_size[G|M|K]) [file_pattern...]\n\n", argv[0]);
        fprintf(stdout, "Omitting the file_pattern will just print the target size in Bytes.\n\n");
        fprintf(stdout, "Set environment variable DISKFIT_STRIPDIR to any value "
                "to strip directories.\n");

        return EXIT_FAILURE;
    } else if (argc == 2) {
        fprintf(stdout, "%" G_GUINT64_FORMAT "\n", diskfit_target_size(argv[1]));
        return EXIT_SUCCESS;
    } else {

        int i;
        size_t j, nitems = 0;
        FITEM *fitems = NULL;
        guint64 tsize = 0u;
        const guint64 tg = diskfit_target_size(argc > 1 ? argv[1] : "dvd");
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

                CANDIDATES = g_tree_new(eq);

                diskfit_get_candidates(fitems, nitems, tsize, tg, addCandidate);
                DISP_PARAMS p = { getenv("DISKFIT_STRIPDIR") != NULL, tg };

                g_tree_foreach(CANDIDATES, display_candidates, &p);
                g_tree_destroy(CANDIDATES);
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

    return EXIT_SUCCESS;
}

// kate: indent-mode cstyle; indent-width 4; replace-tabs on; 
