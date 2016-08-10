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

#include "diskfit.h"

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

static off_t sum(const FITEM *item, int n) {

    int i;
    off_t sum = 0;

    for (i = 0; i < n; ++i) {
        sum += item[i].fsize;
    }

    return sum;
}

static void swap(FITEM *restrict a, FITEM *restrict b) {

    if (a != b) {
        FITEM h;

        memcpy(&h, b, sizeof(FITEM));
        memcpy(b,  a, sizeof(FITEM));
        memcpy(a, &h, sizeof(FITEM));
    }
}

static void permute(FITEM *array, int i, int length, off_t target, ADDER adder,
                    unsigned long *it_cur, unsigned long it_tot) {

    if (length == i) {

        int k = length - 1;
        off_t s = 0;

        while (k >= 0 && (s = sum(array, k + 1)) > target) {
            --k;
        }

        if (s != 0 && s <= target) {
            adder(array, k + 1, s, ++(*it_cur), it_tot);
        }

        return;
    }

    int j = i;

    for (j = i; j < length; ++j) {
        swap(array + i, array + j);
        permute(array, i + 1, length, target, adder, it_cur, it_tot);
        swap(array + i, array + j);
    }

    return;
}

static unsigned long fak(int n) {

    int i;
    unsigned long fak;

    for (i = 1, fak = 1; i <= n; ++i) {
        fak *= i;
    }

    return fak;
}

void diskfit_get_candidates(FITEM *array, int length, off_t target, ADDER adder) {

    unsigned long cur = 0ul;

    permute(array, 0, length, target, adder, &cur, fak(length));
}

const char *diskfit_hrsize(off_t s) {

    char *r = malloc(1024 * sizeof(char));
    const double d = log(s) / M_LN2;

    if (d >= 30.0) {
        snprintf(r, 1023, "%.2f GByte", (float) s / 1073741824.0f);
    } else if (d >= 20.0) {
        snprintf(r, 1023, "%.2f MByte", (float) s / 1048576.0f);
    } else if (d >= 10.0) {
        snprintf(r, 1023, "%.2f KByte", (float) s / 1024.0f);
    } else {
        snprintf(r, 1023, "%ld Byte", s);
    }

    return r;
}

off_t diskfit_target_size(const char *tgs) {

    char suff = '\0';
    double fac = 1.0;

    if (!strncasecmp(tgs, "dvd", 3)) {
        return 4707319808L;
    }

    if (!strncasecmp(tgs, "cd", 2)) {
        return 734003200L;
    }

    double b = 0.0;

    if (sscanf(tgs, "%lf%c", &b, &suff) != EOF) {

        switch (suff) {
            case 'G':
            case 'g':
                fac = 1073741824L;
                break;

            case 'M':
            case 'm':
                fac = 1048576L;
                break;

            case 'K':
            case 'k':
                fac = 1024L;
                break;
        }
    }

    return b * fac;
}

// kate: indent-mode cstyle; indent-width 4; replace-tabs on; 
