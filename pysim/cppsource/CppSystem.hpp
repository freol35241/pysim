//   Copyright (c) 2014-2016 SSPA Sweden AB

#pragma once

#include "CommonSystemImpl.hpp"
#include "PysimTypes.hpp"
#include <Eigen/Dense>

#include <vector>
#include <map>
#include <string>

namespace pysim {

class CppSystem :
    public CommonSystemImpl
{
public:
    CppSystem();
    virtual ~CppSystem();

    //  Inherited from System
    virtual void preSim(){};
    virtual void preStep() {};
    virtual void doStep(double time)=0;
    virtual void postStep() {};

protected:

    ///////////////////////////////////////
    //
    //      Cpp Interface
    //
    ///////////////////////////////////////

    void par(std::vector<double>* vars, const char* name, const char* desc);
    void par(std::vector<std::vector<double>>* vars, const char* name, const char* desc);
    void par(std::string*, const char* name, const char* description);
    void par(std::map<std::string, double>*, const char* name, const char* description);
    void par(std::map<std::string, std::vector<double>>* var, const char* name, const char* description);
    //void par(pysim::matrix* vars, const char* name, const char* description);

    void input(double* var, const char* name, const char* desc);
    void input(pysim::vector* vars, const char* name, const char* description);
    void input(pysim::matrix*  vars, const char* name, const char* description);

    void output(double* var, const char* name, const char* desc);
    void output(pysim::vector* vars, const char* name, const char* desc);
    void output(pysim::matrix* vars, const char* name, const char* desc);

    void state(double* state, const char* stateName, double* der, const char* derName, const char* desc = "");
    void state(pysim::vector* state, const char* stateName, pysim::vector* der, const char* derName, const char* desc = "");
    void state(pysim::matrix* state, const char* stateName, pysim::matrix* der, const char* derName, const char* desc = "");


    void setNextUpdate(double t);
    void setDiscrete(bool d = true);

};

#define STATE(x,dx,s) state(&x,#x,&dx,#dx,s);

#define INPUT(x,s) input(&x,#x,s);
#define OUTPUT(x,s) output(&x,#x,s);

#define PAR(x,s) par(&x,#x,s);
}