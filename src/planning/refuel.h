#ifndef REFUEL_H
#define REFUEL_H
#include <iostream>

const int rmaxm=64, rmaxc=1001, rinf=1000000000;
static int rdp[rmaxm+1][rmaxc];
static short rpf[rmaxm+1][rmaxc], rpa[rmaxm+1][rmaxc];
long long rstates=0;

// m stops (0..m-1) then destination m. d[j]=fuel stop j -> j+1. st[j]=station available.
// returns min extra stop time or -1 if infeasible. buy[j]=units bought at stop j.
int refueldp(int m,const int* d,const bool* st,int cap,int f0,int maxbuy,int stime,int* buy){
    rstates=0;
    if(m>rmaxm || cap>=rmaxc || f0>cap || f0<0) return -1;
    for(int j=0;j<=m;j++) for(int f=0;f<=cap;f++) rdp[j][f]=rinf;
    rdp[0][f0]=0;
    for(int j=0;j<m;j++){
        for(int f=0;f<=cap;f++){
            if(rdp[j][f]>=rinf) continue;
            int amax=0;
            if(st[j]){ amax=cap-f; if(maxbuy<amax) amax=maxbuy; }
            for(int a=0;a<=amax;a++){
                rstates++;
                if(f+a<d[j]) continue;
                int nf=f+a-d[j], c=rdp[j][f]+(a>0?stime:0);
                if(c<rdp[j+1][nf]){ rdp[j+1][nf]=c; rpf[j+1][nf]=f; rpa[j+1][nf]=a; }
            }
        }
    }
    int bf=-1;
    for(int f=0;f<=cap;f++) if(rdp[m][f]<rinf && (bf<0 || rdp[m][f]<rdp[m][bf])) bf=f;
    if(bf<0) return -1;
    int best=rdp[m][bf], f=bf;
    for(int j=m;j>=1;j--){ buy[j-1]=rpa[j][f]; f=rpf[j][f]; }
    return best;
}
#endif
