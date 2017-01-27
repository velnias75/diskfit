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

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <inttypes.h>

#include "diskfit.h"
#include "fitem.h"

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

typedef struct {
    DISKFIT_FITEM   *array;
    size_t           length;
    uint64_t         total;
    uint64_t         target;
    DISKFIT_INSERTER adder;
    mpz_ptr          it_cur;
    mpz_srcptr       it_tot;
    void            *user_data;
} PERMUTE_ARGS;

static inline void swap(DISKFIT_FITEM *restrict a, DISKFIT_FITEM *restrict b) {

    if (a != b) {

        DISKFIT_FITEM h;

        memmove(&h, b, sizeof(DISKFIT_FITEM));
        memmove(b,  a, sizeof(DISKFIT_FITEM));
        memmove(a, &h, sizeof(DISKFIT_FITEM));
    }
}

static inline void add(const PERMUTE_ARGS *const pa) {

    int k = pa->length;
    uint64_t s = pa->total;

    while (k >= 0 && (s -= pa->array[--k].fsize) > pa->target);

    mpz_add_ui(pa->it_cur, pa->it_cur, 1UL);

    if (pa->adder && s != 0 && s <= pa->target) {
        pa->adder(pa->array, k, s, pa->it_cur, pa->it_tot, pa->user_data);
    }
}

static void permute(const PERMUTE_ARGS *const pa) {

    unsigned int *p = malloc((pa->length + 1) * sizeof(int));

    if (p) {

        unsigned int i, j;

        for (i = 0; i < pa->length; ++i) {
            p[i] = i;
        }

        p[pa->length] = pa->length;

        add(pa);

        i = 1;

        while (i < pa->length) {

            --p[i];

            j = (i & 1) * p[i];

            swap(&(pa->array[j]), &(pa->array[i]));
            add(pa);

            i = 1;

            while (!p[i]) {
                p[i] = i;
                ++i;
            }
        }

        free(p);
    }
}

void diskfit_get_candidates(DISKFIT_FITEM *array, size_t length, uint64_t total, uint64_t target,
                            DISKFIT_INSERTER adder, void *user_data) {
    if (array) {

        mpz_t it_cur, it_tot;

        if (total > target) {

            mpz_init(it_tot);
            mpz_init_set_ui(it_cur, 0UL);
            mpz_fac_ui(it_tot, length);

            const PERMUTE_ARGS pa = { array, length, total, target, adder, it_cur, it_tot,
                                      user_data
                                    };
            permute(&pa);

        } else {

            mpz_init_set_ui(it_cur, 1UL);
            mpz_init_set_ui(it_tot, 1UL);

            adder(array, length, total, it_cur, it_tot, user_data);
        }

        mpz_clear(it_cur);
        mpz_clear(it_tot);
    }
}

int diskfit_hrsize(uint64_t s, char *out, size_t len) {

    if (out) {

        const double d = log(s) / M_LN2;

        if (d >= 30.0) {
            return snprintf(out, len, "%.2f GByte", (float) s / 1073741824.0f);
        } else if (d >= 20.0) {
            return snprintf(out, len, "%.2f MByte", (float) s / 1048576.0f);
        } else if (d >= 10.0) {
            return snprintf(out, len, "%.2f KByte", (float) s / 1024.0f);
        } else {
            return snprintf(out, len, "%" PRIu64 " Byte", s);
        }
    }

    return -1;
}

uint64_t diskfit_target_size(const char *tgs, DISKFIT_TARGETMAPPER tmp, void *user_data) {

    if (tgs) {

        uint64_t t = 0u;

        if (tmp && tmp(tgs, &t, user_data)) {
            return t;
        } else {

            char suff = '\0';
            double fac = 1.0;

            if ((tgs[0] == 'D' || tgs[0] == 'd') && (tgs[1] == 'V' || tgs[1] == 'v') &&
                    (tgs[2] == 'D' || tgs[2] == 'd')) {
                return 4705954816u;
            }

            if ((tgs[0] == 'C' || tgs[0] == 'c') && (tgs[1] == 'D' || tgs[1] == 'd')) {
                return 734003200u;
            }

            double b = 0.0;

            if (sscanf(tgs, "%lf%c", &b, &suff) != EOF) {

                switch (suff) {
                    case 'G':
                    case 'g':
                        fac = 1073741824.0;
                        break;

                    case 'M':
                    case 'm':
                        fac = 1048576.0;
                        break;

                    case 'K':
                    case 'k':
                        fac = 1024.0;
                        break;
                }
            }

            return b * fac;
        }
    }

    return 0u;
}

// kate: indent-mode cstyle; indent-width 4; replace-tabs on; 
