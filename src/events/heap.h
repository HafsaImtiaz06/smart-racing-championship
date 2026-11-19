#ifndef EVHEAP_H
#define EVHEAP_H
#include <iostream>

struct ev{int id,type,t,pri,seq,target,val,dur,isexp,eff;};

struct evheap{
    ev* a; int n,cap;
    long long cmps,swaps,pushes,pops;
    void init(int c){ a=new ev[c]; n=0; cap=c; cmps=swaps=pushes=pops=0; }
    void freeh(){ delete[] a; a=0; }
    bool lt(const ev& x,const ev& y){
        cmps++;
        if(x.t!=y.t) return x.t<y.t;
        if(x.pri!=y.pri) return x.pri<y.pri;
        return x.seq<y.seq;
    }
    bool push(const ev& e){
        if(n==cap) return false;
        int i=n++; a[i]=e; pushes++;
        while(i>0){
            int p=(i-1)/2;
            if(!lt(a[i],a[p])) break;
            ev t=a[i]; a[i]=a[p]; a[p]=t; swaps++; i=p;
        }
        return true;
    }
    ev& top(){ return a[0]; }
    ev pop(){
        ev r=a[0]; a[0]=a[--n]; pops++;
        int i=0;
        for(;;){
            int l=2*i+1, rr=l+1, m=i;
            if(l<n && lt(a[l],a[m])) m=l;
            if(rr<n && lt(a[rr],a[m])) m=rr;
            if(m==i) break;
            ev t=a[i]; a[i]=a[m]; a[m]=t; swaps++; i=m;
        }
        return r;
    }
};
#endif
