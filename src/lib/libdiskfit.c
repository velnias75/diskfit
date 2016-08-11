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

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <inttypes.h>

#include "diskfit.h"

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

typedef struct {
    FITEM *array;
    size_t length;
    uint64_t total;
    uint64_t target;
    INSERTER adder;
    unsigned long *it_cur;
    unsigned long it_tot;
} PERMUTE_ARGS;

inline static void swap(FITEM *restrict a, FITEM *restrict b) {

    if (a != b) {

        FITEM h;

        memcpy(&h, b, sizeof(FITEM));
        memcpy(b,  a, sizeof(FITEM));
        memcpy(a, &h, sizeof(FITEM));
    }
}

static void permute(const PERMUTE_ARGS *const pa, size_t i) {

    if (pa->length == i) {

        int k = pa->length;
        uint64_t s = pa->total;

        while (k >= 0 && (s -= pa->array[--k].fsize) > pa->target);

        ++(*pa->it_cur);

        if (pa->adder && s != 0 && s <= pa->target) {
            pa->adder(pa->array, k, s, *pa->it_cur, pa->it_tot);
        }

        return;
    }

    size_t j = i;

    for (j = i; j < pa->length; ++j) {
        swap(pa->array + i, pa->array + j);
        permute(pa, i + 1);
        swap(pa->array + i, pa->array + j);
    }

    return;
}

inline static unsigned long fak(int n) {

    int i;
    unsigned long fak;

    for (i = 1, fak = 1; i <= n; ++i) {
        fak *= i;
    }

    return fak;
}

void diskfit_get_candidates(FITEM *array, size_t length, uint64_t total, uint64_t target,
                            INSERTER adder) {

    if (array) {

        if (total > target) {

            unsigned long cur = 0ul;

            const PERMUTE_ARGS pa = { array, length, total, target, adder, &cur, fak(length) };

            permute(&pa, 0);

        } else {
            adder(array, length, total, 1, 1);
        }
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

uint64_t diskfit_target_size(const char *tgs) {

    if (tgs) {

        char suff = '\0';
        double fac = 1.0;

        if (!strncasecmp(tgs, "dvd", 3)) {
            return 4705954816u;
        }

        if (!strncasecmp(tgs, "cd", 2)) {
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

    return 0u;
}

// kate: indent-mode cstyle; indent-width 4; replace-tabs on; 
