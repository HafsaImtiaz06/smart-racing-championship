#include <iostream>
#include "../src/generation/trackgen.h"
using namespace std;

// input: seed n k f p nobs nshort nextra noneway radius maxlen maxdeg sgap maxtries maxnodes
int main(){
    unsigned seed;
    cin>>seed>>gp.n>>gp.k>>gp.f>>gp.p>>gp.nobs>>gp.nshort>>gp.nextra>>gp.noneway>>gp.radius>>gp.maxlen>>gp.maxdeg>>gp.sgap>>gp.maxtries>>gp.maxnodes;
    int rej=0;
    for(int t=0;t<gp.maxtries;t++){
        int r=attempt(seed+t);
        cout<<"try "<<t<<" seed "<<seed+t<<": "<<vmsg[r]<<" | nodes "<<gnodes<<" prunes";
        for(int i=1;i<8;i++) cout<<" "<<gprune[i];
        cout<<"\n";
        if(r==0){ cout<<"accepted after "<<rej<<" rejections\n"; dumpjson(); return 0; }
        rej++;
    }
    cout<<"no valid track in "<<gp.maxtries<<" tries\n";
    return 0;
}
