/*
 * Copyright 2020 by Heiko Schäfer <heiko@rangun.de>
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

#ifndef BLOCKING_QUEUE_H
#define BLOCKING_QUEUE_H

#ifdef _cplusplus
extern "C" {
#endif

typedef struct blocking_queue_t blocking_queue_t;

blocking_queue_t *blocking_queue_create(size_t);
void blocking_queue_destroy(blocking_queue_t * const);

void blocking_queue_put(blocking_queue_t *, void *);
void *blocking_queue_take(blocking_queue_t *);

int blocking_queue_isEmpty(blocking_queue_t *);
int blocking_queue_isFull(blocking_queue_t *);

#ifdef _cplusplus
}
#endif

#endif /* BLOCKING_QUEUE_H */

// kate: indent-mode cstyle; indent-width 4; replace-tabs on; remove-trailing-space on;
