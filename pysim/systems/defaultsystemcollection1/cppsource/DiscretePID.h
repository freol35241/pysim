#pragma once
#include "CppSystem.hpp"

class DiscretePID :
    public CppSystem
{
public:
    DiscretePID(void);
    virtual void preSim();
    void doStep(double time);

protected:

    //Parameters
    double stepsize;
    double p,plim,i,d;
    double antiwindup;
    double insig, refsig,dsig;

    //State
    double iPart,dIPart;

    //Outputs
    double outsig;;

};