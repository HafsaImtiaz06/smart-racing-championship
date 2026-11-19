#ifndef KNAPSACK_H
#define KNAPSACK_H
#include <iostream>

const int kmaxn=256, kmaxb=10001;
struct item{int id,c,v;};
static int kdp[kmaxn+1][kmaxb];
long long kstates=0;

int knapdp(const item* it,int m,int b,bool* pick){
    kstates=0;
    for(int j=0;j<=b;j++) kdp[0][j]=0;
    for(int i=1;i<=m;i++){
        int c=it[i-1].c, v=it[i-1].v;
        for(int j=0;j<=b;j++){
            kdp[i][j]=kdp[i-1][j];
            if(c<=j && kdp[i-1][j-c]+v>kdp[i][j]) kdp[i][j]=kdp[i-1][j-c]+v;
            kstates++;
        }
    }
    int j=b;
    for(int i=m;i>=1;i--){
        if(kdp[i][j]!=kdp[i-1][j]){ pick[i-1]=true; j-=it[i-1].c; }
        else pick[i-1]=false;
    }
    return kdp[m][b];
}

static bool kbetter(const item& a,const item& b){
    long long l=(long long)a.v*b.c, r=(long long)b.v*a.c;
    if(l!=r) return l>r;
    return a.id<b.id;
}

// zero-cost positive-benefit first, zero-cost zero-benefit skipped, ratio desc, tie lower id
int knapgreedy(const item* it,int m,int b,bool* pick){
    int ord[kmaxn], n=0, val=0, left=b;
    for(int i=0;i<m;i++){
        pick[i]=false;
        if(it[i].c==0 && it[i].v>0){ pick[i]=true; val+=it[i].v; }
        else if(it[i].c>0 && it[i].v>0) ord[n++]=i;
    }
    for(int i=1;i<n;i++){
        int x=ord[i], j=i-1;
        while(j>=0 && kbetter(it[x],it[ord[j]])){ ord[j+1]=ord[j]; j--; }
        ord[j+1]=x;
    }
    for(int k=0;k<n;k++){
        int i=ord[k];
        if(it[i].c<=left){ pick[i]=true; left-=it[i].c; val+=it[i].v; }
    }
    return val;
}

int knapbrute(const item* it,int m,int b){
    int best=0;
    for(long long mask=0;mask<(1LL<<m);mask++){
        int c=0,v=0;
        for(int i=0;i<m;i++) if((mask>>i)&1){ c+=it[i].c; v+=it[i].v; }
        if(c<=b && v>best) best=v;
    }
    return best;
}
#endif
