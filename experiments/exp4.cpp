#include <iostream>
#include <chrono>
#include "../src/events/evmgr.h"
using namespace std;

unsigned rs;
int rnd(int m){ rs=rs*1664525u+1013904223u; return (int)((rs>>8)%(unsigned)m); }
double now(){ return chrono::duration<double,milli>(chrono::steady_clock::now().time_since_epoch()).count(); }
bool before(const ev& a,const ev& b){
    if(a.t!=b.t) return a.t<b.t;
    if(a.pri!=b.pri) return a.pri<b.pri;
    return a.seq<b.seq;
}

// input: seed nsizes then sizes, then trange (small value forces timestamp ties)
int main(){
    int seed,ns; cin>>seed>>ns;
    int sz[32]; for(int i=0;i<ns;i++) cin>>sz[i];
    int tr; cin>>tr; rs=seed;
    cout<<"n insert_ms extract_ms cmps swaps ordered mgr_ms applied lazy rejected\n";
    for(int s=0;s<ns;s++){
        int n=sz[s];
        evheap h; h.init(n);
        ev* in=new ev[n];
        for(int i=0;i<n;i++){ in[i].id=i; in[i].t=rnd(tr); in[i].pri=1+rnd(6); in[i].seq=i; in[i].type=in[i].pri; }
        double a=now();
        for(int i=0;i<n;i++) h.push(in[i]);
        double ti=now()-a;
        a=now(); ev prev; bool ok=true;
        for(int i=0;i<n;i++){ ev x=h.pop(); if(i && before(x,prev)) ok=false; prev=x; }
        double te=now()-a;
        long long cm=h.cmps, sw=h.swaps;
        h.freeh(); delete[] in;

        evmgr m; m.init(64,64,n);
        for(int i=0;i<64;i++){ m.isshort[i]=true; m.ispick[i]=true; m.setstation(i,true); }
        a=now();
        int* ids=new int[n];
        for(int i=0;i<n;i++){
            int ty=1+rnd(6), val=1, dur=1+rnd(30);
            if(ty==3) val=1+rnd(4); else if(ty==4) val=1+rnd(100); else if(ty==5) val=rnd(2);
            ids[i]=m.add(ty,rnd(tr),rnd(64),val,dur);
        }
        for(int i=0;i<n/10;i++){ int q=ids[rnd(n)]; if(q>0) m.cancel(q); }
        m.run(tr+100);
        double tm=now()-a;
        cout<<n<<" "<<ti<<" "<<te<<" "<<cm<<" "<<sw<<" "<<(ok?"yes":"NO")<<" "<<tm<<" "<<m.napplied<<" "<<m.nlazy<<" "<<m.nrej<<"\n";
        delete[] ids;
    }
    return 0;
}
