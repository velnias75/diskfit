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

#ifndef DISKFIT_H
#define DISKFIT_H

#define DISKFIT_EXPORT __attribute__((visibility ("default")))

#ifdef _cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stddef.h>

#include <gmp.h>

    typedef struct {
        char *fname;
        uint64_t fsize;
    } FITEM;

    typedef void (*INSERTER)(FITEM *fitems, int length, uint64_t total,
                             mpz_t *const it_cur, mpz_t *const it_tot,
                             void *user_data);

    typedef int (*TARGETMAPPER)(const char *tgs, uint64_t *size, void *user_data);

    DISKFIT_EXPORT int diskfit_hrsize(uint64_t size, char *out, size_t len);
    DISKFIT_EXPORT uint64_t diskfit_target_size(const char *tgs, TARGETMAPPER tmp, void *user_data);
    DISKFIT_EXPORT void diskfit_get_candidates(FITEM *fitems, size_t length, uint64_t total,
            uint64_t target, INSERTER inserter, void *user_data);

#ifdef _cplusplus
}
#endif

#endif /* DISKFIT_H */

// kate: indent-mode cstyle; indent-width 4; replace-tabs on; 
