#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <math.h>
#include <wordexp.h>

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

typedef struct {
  char *fname;
  off_t fsize;
} FITEM;

typedef struct {
  FITEM *entries;
  size_t size;
  off_t total;
} FITEMLIST;

typedef void (*FUN)(FITEM *array, int len, off_t total);

FITEMLIST *CANDIDATES = NULL;
size_t CANDIDATES_NUM = 0;

const char *hrsize(off_t s) {
  
  char *r = malloc(1024 * sizeof(char));
  const double d = log(s)/M_LN2;
  
  if(d >= 30.0) {
    snprintf(r, 1023, "%.2f GByte", (float)s/1073741824.0f);
  } else if(d >= 20.0) {
    snprintf(r, 1023, "%.2f MByte", (float)s/1048576.0f);
  } else if(d >= 10.0) {
    snprintf(r, 1023, "%.2f KByte", (float)s/1024.0f);
  } else {
    snprintf(r, 1023, "%ld Byte", s);
  }
  
  return r;
}

off_t sum(FITEM *item, int n) {
  
  int i;
  off_t sum = 0;
  
  for(i = 0; i < n; ++i) sum += item[i].fsize;
  
  return sum;
}

void swap(FITEM *a, FITEM *b) {
  
  FITEM h = { b->fname, b->fsize };

  b->fname = a->fname;
  b->fsize = a->fsize;
  
  a->fname = h.fname;
  a->fsize = h.fsize;
}

void permute(FITEM *array, int i, int length, off_t target, FUN foo) { 
  
  int k = length - 1;
  off_t s = 0;
  
  if(length == i) {
    
    while(k >= 0 && (s = sum(array, k + 1)) > target) --k;
    
    if(s <= target) foo(array, k + 1, s);
    
    return;
  }
  
  int j = i;
  
  for(j = i; j < length; ++j) { 
    swap(array + i, array + j);
    permute(array, i + 1, length, target, foo);
    swap(array + i, array + j);
  }
  
  return;
}

int fitem_cmp(const void *a, const void *b) {
  return strcmp(((FITEM *)a)->fname, ((FITEM *)b)->fname);
}

int cand_cmp(const void *a, const void *b) {
  //return strcmp(((FITEM *)a)->fname, ((FITEM *)b)->fname);
  
  if(((FITEMLIST *)a)->total < ((FITEMLIST *)b)->total) return -1;
  if(((FITEMLIST *)a)->total > ((FITEMLIST *)b)->total) return 1;
  
  return 0;
}

void addCandidate(FITEM *array, int len, off_t total) {
  
  if(total == 0) return;
  
  int i;
  size_t j, k;
  FITEMLIST l = { malloc(len * sizeof(FITEM)), len, total };
  
  for(i = 0; i < len; ++i) {
    memcpy(&(l.entries[i]), &(array[i]), sizeof(FITEM));
  }
  
  qsort(l.entries, l.size, sizeof(FITEM), fitem_cmp);
  
  if(!CANDIDATES) {
    CANDIDATES = malloc(sizeof(FITEMLIST));
  } else {
    
    for(j = 0; j < CANDIDATES_NUM; ++j) {
      
      if(CANDIDATES[j].size == l.size && CANDIDATES[j].total == l.total) {
	
	int dup = 0;
	
	for(k = 0; k < l.size; ++k) {
	  dup |= (CANDIDATES[j].entries[k].fsize == l.entries[k].fsize && 
		  !strcmp(CANDIDATES[j].entries[k].fname, l.entries[k].fname));
	}
	
	if(dup) {
	  free(l.entries);
	  return;
	}
      }
    }
    
    CANDIDATES = realloc(CANDIDATES, (CANDIDATES_NUM + 1) * sizeof(FITEMLIST));
  }
  
  memcpy(&(CANDIDATES[CANDIDATES_NUM]), &l, sizeof(FITEMLIST));
  
  ++CANDIDATES_NUM;
}

int main(int argc, char *argv[]) {
  
  size_t j, l;
  int i, nitems = 0;
  FITEM *fitems = NULL;
  off_t tsize = 0, tg = argc > 1 ? atol(argv[1]) : 0L;
  const char *hr_tot, *hr_tg;
  struct stat st;
  
  fprintf(stderr, PACKAGE_STRING " - (c) 2016 by Heiko Schaefer <heiko@rangun.de>\n");
  
  if(argc < 3) {
    
    fprintf(stderr, "Usage: %s target_size files...\n", argv[0]);
    return EXIT_FAILURE;
    
  } else {
    
    wordexp_t p;
    
    memset(&p, 0, sizeof(wordexp_t));
    
    tg = tg == 0 ? 4724464025 : tg;
    
    for(i = 0; i < argc - 2; ++i) wordexp(argv[i+2], &p, WRDE_NOCMD|WRDE_APPEND);
    
    fitems = calloc(p.we_wordc, sizeof(FITEM));
      
    for(j = 0; j < p.we_wordc; ++j) {
      
      if(!stat(p.we_wordv[j], &st)) {
      
	tsize += st.st_size;
	
	fitems[j].fname = p.we_wordv[j];
	fitems[j].fsize = st.st_size;
	
	++nitems;
      }
    }
    
    permute(fitems, 0, nitems, tg, addCandidate);
    
    qsort(CANDIDATES, CANDIDATES_NUM, sizeof(FITEMLIST), cand_cmp);
    
    for(j = 0; j < CANDIDATES_NUM; ++j) {
      
      const char *hrs;
      
      fprintf(stdout, "[ ");
	
      for(l = 0; l < CANDIDATES[j].size; ++l) {
	fprintf(stdout, "'%s' ", CANDIDATES[j].entries[l].fname);
      }
      
      fprintf(stdout, "] = %s\n", (hrs = hrsize(CANDIDATES[j].total)));
      
      free((void *)hrs);
      free(CANDIDATES[j].entries);
    }
    
    free(fitems);
    free(CANDIDATES);
    
    wordfree(&p);
    
    fprintf(stderr, "Total size: %s - Target size: %s\n", 
	    (hr_tot = hrsize(tsize)), (hr_tg = hrsize(tg)));
    
    free((void *)hr_tot);
    free((void *)hr_tg);
  }
  
  return EXIT_SUCCESS;
}