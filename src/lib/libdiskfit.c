/*
 * Copyright 2016-2018 by Heiko Schäfer <heiko@rangun.de>
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
#include <inttypes.h>

#include "diskfit.h"
#include "fitem.h"

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gsl/gsl_combination.h>

typedef struct {
    DISKFIT_FITEM         *const array;
    const gsl_combination *combination;
    const size_t           c_index;
    const size_t           length;
    const uint64_t         total;
    const uint64_t         target;
    DISKFIT_INSERTER       adder;
    DISKFIT_PROGRESS       progress;
    const mpz_ptr          it_cur;
    const mpz_srcptr       it_tot;
    const mp_bitcnt_t      div_by;
    volatile int          *const interrupted;
    void                  *const user_data;
} PERMUTE_ARGS;

static DISKFIT_ALLOC _diskfit_mem_alloc = malloc;
static DISKFIT_FREE  _diskfit_mem_free  = free;

static inline void add(const PERMUTE_ARGS *const pa) {

    if (!*pa->interrupted) {

        register const size_t ck = gsl_combination_k(pa->combination);

        if (ck) {

            uint64_t cs = 0u;

            for (register size_t ci = 0; ci < ck; ++ci) {
                cs += pa->array[gsl_combination_get(pa->combination, ci)].fsize;
            }

            mpz_add_ui(pa->it_cur, pa->it_cur, 1UL);
            pa->progress(pa->it_cur, pa->it_tot, pa->div_by, pa->user_data);

            if (cs != 0 && cs <= pa->target && pa->adder) {

                DISKFIT_FITEM *const p = _diskfit_mem_alloc(ck * sizeof(DISKFIT_FITEM));

                for (register size_t ci = 0; ci < ck; ++ci) {
                    memcpy(&p[ci], &pa->array[gsl_combination_get(pa->combination, ci)],
                       sizeof(DISKFIT_FITEM));
                }

                pa->adder(p, ck, cs, pa->user_data);
                _diskfit_mem_free(p);
            }
        }
    }
}

int diskfit_get_candidates(DISKFIT_FITEM *array, size_t length, uint64_t total, 
                           uint64_t target, DISKFIT_INSERTER adder, 
                           DISKFIT_PROGRESS progress, void *user_data, 
                           volatile int *interrupted) {
    if (array) {

        mpz_t it_cur, it_tot, aux;
        mp_bitcnt_t div_by = 1UL;

        if (total > target) {

            mpz_init(aux);
            mpz_init_set_ui(it_tot, 0UL);
            mpz_init_set_ui(it_cur, 0UL);

            gsl_combination *c;
            register size_t i;

            for (i = 0; i < length; i++) {
                mpz_bin_uiui(aux, length, i);
                mpz_add(it_tot, it_tot, aux);
            }

            mpz_mul_2exp(it_tot, it_tot, 1U);

            if(mpz_cmp_ui(it_tot, 1024UL) > 0) {
                
                mpz_tdiv_q_2exp(aux, it_tot, 9UL);
                
                while(!mpz_divisible_2exp_p(aux, 10UL)) {
                    mpz_add_ui(aux, aux, 1UL);
                }
                
                div_by = 0UL;
                
                do {
                    mpz_div_2exp(aux, aux, 1UL);
                    ++div_by;
                } while(mpz_cmp_ui(aux, 1UL));
            }

            mpz_clear(aux);

            for (i = 0; i <= length && !(*interrupted); i++) {

                c = gsl_combination_calloc(length, i);

                const PERMUTE_ARGS pa = { array, c, i, length, total, target, adder, progress,
                                              it_cur, it_tot, div_by, interrupted, user_data };
                do {
                    add(&pa);
                } while (gsl_combination_next(c) == GSL_SUCCESS && !(*interrupted));

                gsl_combination_free(c);
            }

        } else {

            mpz_init_set_ui(it_cur, 1UL);
            mpz_init_set_ui(it_tot, 1UL);

            adder(array, length, total, user_data);
        }

        mpz_clear(it_cur);
        mpz_clear(it_tot);
    }

    return *interrupted;
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

void diskfit_set_mem_funcs(DISKFIT_ALLOC a, DISKFIT_FREE f) {
    _diskfit_mem_alloc = a ? a : malloc;
    _diskfit_mem_free  = f ? f : free;
}

// kate: indent-mode cstyle; indent-width 4; replace-tabs on;
