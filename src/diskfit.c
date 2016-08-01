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

void permute(FITEM *array, int i, int length, off_t target) { 
  
  int l, k = length - 1;
  const char *hrs;
  off_t s = 0;
  
  if(length == i) {
    
    while(k >= 0 && (s = sum(array, k + 1)) > target) --k;
    
    if(s <= target) {
      fprintf(stdout, "[ ");
      for(l = 0; l < k + 1; ++l) fprintf(stdout, "'%s' ", array[l].fname);
      fprintf(stdout, "] = %s\n", (hrs = hrsize(s)));
      free((void *)hrs);
    }
    
    return;
  }
  
  int j = i;
  
  for(j = i; j < length; ++j) { 
    swap(array + i, array + j);
    permute(array, i + 1, length, target);
    swap(array + i, array + j);
  }
  
  return;
}

int main(int argc, char *argv[]) {
  
  size_t j;
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
    
    permute(fitems, 0, nitems, tg);
    
    free(fitems);
    wordfree(&p);
    
    fprintf(stderr, "Total size: %s - Target size: %s\n", 
	    (hr_tot = hrsize(tsize)), (hr_tg = hrsize(tg)));
    
    free((void *)hr_tot);
    free((void *)hr_tg);
  }
  
  return EXIT_SUCCESS;
}