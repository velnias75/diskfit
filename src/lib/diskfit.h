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

#define DISKFIT_EXPORT __attribute__((visibility ("default")))

#ifdef _cplusplus
extern "C" {
#endif

#include <sys/types.h>

typedef struct {
    char *fname;
    off_t fsize;
} FITEM;

typedef void (*ADDER)(FITEM *array, int len, off_t total, 
                      const unsigned long it_cur, const unsigned long it_tot);

DISKFIT_EXPORT const char *diskfit_hrsize(off_t s);
DISKFIT_EXPORT off_t diskfit_target_size(const char *tgs);
DISKFIT_EXPORT void diskfit_get_candidates(FITEM *array, int length, off_t target, ADDER adder);

#ifdef _cplusplus
}
#endif
    
// kate: indent-mode cstyle; indent-width 4; replace-tabs on; 
