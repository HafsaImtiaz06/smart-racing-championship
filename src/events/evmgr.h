#ifndef EVMGR_H
#define EVMGR_H
#include <iostream>
#include "heap.h"

// types: 1 blockage, 2 shortcut toggle, 3 oil spill, 4 speed restriction, 5 station availability, 6 nitro booster
// priority = type. val: t1/t2 1=apply 0=clear, t3 difficulty penalty 1..4, t4 speed cap percent 1..100,
// t5 1=force on 0=force off, t6 unused. dur>0 auto-expiry, dur=0 until reversed/cancelled/collected.
// effective state rule: blocked if any t1/t2 active; oil=max penalty; cap=min cap; station off beats on.
// events refer to ids from add(); expiry events get their own ids (isexp=1).

struct eff{int type,target,val,next,on,expid;};
struct logrec{int t,id,type,target,act;}; // act: 0 applied,1 expired,2 cleared,3 ignored,4 lazy-dropped

struct evmgr{
    enum{maxlg=256};
    evheap h;
    int ne,nv,evcap,idcap,nid,nseq,now,nuser;
    bool *canc,*isshort,*isstn,*ispick,*basestn,*blk,*stn,*pick;
    eff* ef;
    int *headE,*headV,*oil,*cap;
    logrec* lg; int nlg;
    long long nrej,nlazy,napplied,ninvalid;
    void (*cb)(int);

    void init(int ne_,int nv_,int evcap_){
        ne=ne_; nv=nv_; evcap=evcap_; idcap=2*evcap+8;
        h.init(idcap);
        canc=new bool[idcap](); ef=new eff[idcap]();
        headE=new int[ne]; headV=new int[nv];
        for(int i=0;i<ne;i++) headE[i]=-1;
        for(int i=0;i<nv;i++) headV[i]=-1;
        isshort=new bool[ne](); blk=new bool[ne](); oil=new int[ne](); cap=new int[ne];
        for(int i=0;i<ne;i++) cap[i]=100;
        isstn=new bool[nv](); ispick=new bool[nv](); basestn=new bool[nv](); stn=new bool[nv](); pick=new bool[nv]();
        lg=new logrec[maxlg]; nlg=0;
        nid=1; nseq=0; now=0; nuser=0;
        nrej=nlazy=napplied=ninvalid=0; cb=0;
    }
    void setstation(int v,bool base){ isstn[v]=true; basestn[v]=base; stn[v]=base; }

    void note(int t,int id,int ty,int tg,int act){
        logrec& r=lg[nlg%maxlg]; r.t=t; r.id=id; r.type=ty; r.target=tg; r.act=act; nlg++;
    }

    // returns event id or -1 if rejected
    int add(int type,int t,int target,int val,int dur){
        bool bad=false;
        if(type<1||type>6||t<now||dur<0||nuser>=evcap) bad=true;
        else if(type<=4){
            if(target<0||target>=ne) bad=true;
            else if(type==2 && !isshort[target]) bad=true;
        } else {
            if(target<0||target>=nv) bad=true;
            else if(type==5 && !isstn[target]) bad=true;
            else if(type==6 && !ispick[target]) bad=true;
        }
        if(!bad){
            if((type==1||type==2||type==5) && val!=0 && val!=1) bad=true;
            if(type==3 && (val<1||val>4||dur==0)) bad=true;
            if(type==4 && (val<1||val>100||dur==0)) bad=true;
        }
        if(bad){ nrej++; return -1; }
        ev e; e.id=nid++; e.type=type; e.t=t; e.pri=type; e.seq=nseq++;
        e.target=target; e.val=val; e.dur=dur; e.isexp=0; e.eff=0;
        h.push(e); nuser++;
        return e.id;
    }

    void rece(int e){
        bool b=false; int o=0,c=100,prev=-1,i=headE[e];
        while(i!=-1){
            eff& f=ef[i]; int nx=f.next;
            if(!f.on){ if(prev==-1) headE[e]=nx; else ef[prev].next=nx; }
            else {
                prev=i;
                if(f.type<=2) b=true;
                else if(f.type==3){ if(f.val>o) o=f.val; }
                else if(f.val<c) c=f.val;
            }
            i=nx;
        }
        blk[e]=b; oil[e]=o; cap[e]=c;
    }
    void recv(int v){
        bool fz=false,fo=false,pk=false; int prev=-1,i=headV[v];
        while(i!=-1){
            eff& f=ef[i]; int nx=f.next;
            if(!f.on){ if(prev==-1) headV[v]=nx; else ef[prev].next=nx; }
            else {
                prev=i;
                if(f.type==5){ if(f.val==0) fz=true; else fo=true; }
                else pk=true;
            }
            i=nx;
        }
        stn[v]=fz?false:(fo?true:basestn[v]);
        pick[v]=pk;
    }
    void rec(int type,int target){ if(type<=4) rece(target); else recv(target); }

    void addeff(const ev& x){
        eff& e=ef[x.id];
        e.type=x.type; e.target=x.target; e.val=x.val; e.on=1; e.expid=0;
        if(x.type<=4){ e.next=headE[x.target]; headE[x.target]=x.id; }
        else { e.next=headV[x.target]; headV[x.target]=x.id; }
        if(x.dur>0){
            ev y; y.id=nid++; y.type=x.type; y.pri=x.type; y.seq=nseq++;
            y.t=x.t+x.dur; y.target=x.target; y.val=0; y.dur=0; y.isexp=1; y.eff=x.id;
            h.push(y); e.expid=y.id;
        }
    }
    int clear(int type,int target){
        int c=0, i=(type<=4)?headE[target]:headV[target];
        while(i!=-1){
            eff& f=ef[i];
            if(f.on && f.type==type){ f.on=0; if(f.expid) canc[f.expid]=true; c++; }
            i=f.next;
        }
        return c;
    }

    bool applyev(const ev& x){
        if(canc[x.id]){ nlazy++; note(x.t,x.id,x.type,x.target,4); return false; }
        if(x.isexp){
            eff& e=ef[x.eff];
            if(!e.on) return false;
            e.on=0; rec(e.type,e.target);
            note(x.t,x.id,x.type,x.target,1);
            return true;
        }
        if((x.type==1||x.type==2) && x.val==0){
            int c=clear(x.type,x.target);
            if(!c){ ninvalid++; note(x.t,x.id,x.type,x.target,3); return false; }
            rec(x.type,x.target);
            note(x.t,x.id,x.type,x.target,2);
            return true;
        }
        addeff(x); rec(x.type,x.target);
        napplied++; note(x.t,x.id,x.type,x.target,0);
        return true;
    }

    // applies every event with t<=tnow in heap order; one cb per distinct trigger time (reroute once per group)
    int run(int tnow){
        int groups=0;
        while(h.n>0 && h.top().t<=tnow){
            int t=h.top().t; bool any=false;
            while(h.n>0 && h.top().t==t){ ev x=h.pop(); if(applyev(x)) any=true; }
            if(any){ groups++; if(cb) cb(t); }
        }
        if(tnow>now) now=tnow;
        return groups;
    }

    bool cancel(int id){
        if(id<1||id>=nid||canc[id]) return false;
        canc[id]=true;
        eff& e=ef[id];
        if(e.type!=0 && e.on){
            e.on=0; if(e.expid) canc[e.expid]=true;
            rec(e.type,e.target);
        }
        return true;
    }
    int collect(int v){ int c=clear(6,v); recv(v); return c; }

    bool blocked(int e){ return blk[e]; }
    int status(int e){ return blk[e]?2:((oil[e]>0||cap[e]<100)?1:0); }
    int oilpen(int e){ return oil[e]; }
    int speedcap(int e){ return cap[e]; }
    bool stationon(int v){ return stn[v]; }
    bool pickupon(int v){ return pick[v]; }
    int pending(){ return h.n; }

    void printlog(){
        const char* an[]={"applied","expired","cleared","ignored","lazy-dropped"};
        int s=nlg>maxlg?nlg-maxlg:0;
        for(int i=s;i<nlg;i++){
            logrec& r=lg[i%maxlg];
            std::cout<<"t="<<r.t<<" id="<<r.id<<" type="<<r.type<<" target="<<r.target<<" "<<an[r.act]<<"\n";
        }
    }
};
#endif
