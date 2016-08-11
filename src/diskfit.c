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

typedef struct {
    FITEM *entries;
    size_t size;
    uint64_t total;
} FITEMLIST;

FITEMLIST *CANDIDATES = NULL;
size_t CANDIDATES_NUM = 0;
unsigned long FAK_LST = 0u;

inline static int fitem_cmp(const void *a, const void *b) {
    return strcasecmp(((FITEM *) a)->fname, ((FITEM *) b)->fname);
}

static void addCandidate(FITEM *array, int len, uint64_t total,
                         const unsigned long it_cur, const unsigned long it_tot) {

    FITEMLIST l = { malloc(len * sizeof(FITEM)), len, total };

    if (l.entries) {

        int i;
        const unsigned long fc = (it_cur * 100u) / it_tot;

        if (fc != FAK_LST) {
            fprintf(stderr, "\033[sCalculating: %lu%% ...\033[u", (FAK_LST = fc));
        }

        for (i = 0; i < len; ++i) {
            memcpy(& (l.entries[i]), & (array[i]), sizeof(FITEM));
        }

        qsort(l.entries, l.size, sizeof(FITEM), fitem_cmp);

        if (!CANDIDATES) {
            CANDIDATES = malloc(sizeof(FITEMLIST));
        } else {

            size_t j;

            for (j = 0; j < CANDIDATES_NUM; ++j) {

                if (CANDIDATES[j].size == l.size && CANDIDATES[j].total == l.total) {

                    size_t k;
                    int dup = 0;

                    for (k = 0; k < l.size; ++k) {
                        dup |= CANDIDATES[j].entries[k].fname == l.entries[k].fname;
                    }

                    if (dup) {
                        free(l.entries);
                        return;
                    }
                }
            }

            FITEMLIST *fl = realloc(CANDIDATES, (CANDIDATES_NUM + 1) * sizeof(FITEMLIST));

            if (fl) {
                CANDIDATES = fl;
            } else {
                free(CANDIDATES);
                CANDIDATES = NULL;
            }
        }

        if (CANDIDATES) {
            memcpy(& (CANDIDATES[CANDIDATES_NUM]), &l, sizeof(FITEMLIST));
            ++CANDIDATES_NUM;
        } else {
            error(0, ENOMEM, "%s@%s:%d", __FUNCTION__, __FILE__, __LINE__);
        }
    }
}

int cand_cmp(const void *a, const void *b) {

    if (((FITEMLIST *) a)->total < ((FITEMLIST *) b)->total) {
        return -1;
    }

    if (((FITEMLIST *) a)->total > ((FITEMLIST *) b)->total) {
        return 1;
    }

    return 0;
}

int main(int argc, char *argv[]) {

    fprintf(stderr, PACKAGE_STRING " - (c) 2016 by Heiko Sch\u00e4fer <heiko@rangun.de>\n");

    if (argc < 3) {

        fprintf(stdout, "Usage: %s (cd|dvd|target_size[G|M|K]) file_pattern...\n\n", argv[0]);
        fprintf(stdout, "Set environment variable DISKFIT_STRIPDIR to any value "
                "to strip directories.\n");

        return EXIT_FAILURE;

    } else {

        size_t j;
        int i, nitems = 0;
        FITEM *fitems = NULL;
        uint64_t tsize = 0u;
        const uint64_t tg = diskfit_target_size(argc > 1 ? argv[1] : "dvd");
        char hr_tot[1024], hr_tg[1024];
        wordexp_t p;

        memset(&p, 0, sizeof(wordexp_t));

        for (i = 0; i < argc - 2; ++i) {

            const int wr = wordexp(argv[i + 2], &p, WRDE_NOCMD | WRDE_APPEND);

            if (wr) {
                error(0, wr, "%s@%s:%d", __FUNCTION__, __FILE__, __LINE__);
            }
        }

        if ((fitems = malloc(p.we_wordc * sizeof(FITEM)))) {

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

            fprintf(stderr, "\033[sCalculating: 0%% ...\033[u");
            diskfit_get_candidates(fitems, nitems, tsize, tg, addCandidate);
            qsort(CANDIDATES, CANDIDATES_NUM, sizeof(FITEMLIST), cand_cmp);

            fprintf(stderr, "\033[k");

            const int stripdir = getenv("DISKFIT_STRIPDIR") != NULL;

            for (j = 0; j < CANDIDATES_NUM; ++j) {

                char hrs[1024];
                size_t l;

                fprintf(stdout, "[ ");

                for (l = 0; l < CANDIDATES[j].size; ++l) {

                    char *bc = stripdir ? strdup(CANDIDATES[j].entries[l].fname) :
                               CANDIDATES[j].entries[l].fname;

                    fprintf(stdout, "'%s' ", stripdir ? basename(bc) : bc);

                    if (stripdir) {
                        free(bc);
                    }
                }

                diskfit_hrsize(CANDIDATES[j].total, hrs, 1023);
                fprintf(stdout, "] = %s (%.3f%%)\n", hrs,
                        (float)(CANDIDATES[j].total * 100u) / (float)tg);
                free(CANDIDATES[j].entries);
            }

            free(fitems);
            free(CANDIDATES);

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
