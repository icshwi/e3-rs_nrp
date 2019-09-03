#include <string.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <malloc.h>

#include "registryFunction.h"
#include "aSubRecord.h"
#include "epicsExport.h"

long my_asub_routineDBM(aSubRecord *precord)
{ 
  double arr[precord->noa];  //input parameter
  double zero[precord->noa];                        
  double interval;
  double trigger;
  double offset;

  //double AxisArray[precord->nova];  // output parameter 
  double xtrig[2],ytrig[2];         // trigger display
  //double WattsValues[precord->novd];// transformed measure watts
  
  int i,j;
  long Npoints=0;
 
  memcpy(&arr, (double *)precord->a, precord->noa * sizeof(double));
  memcpy(&interval, (double *)precord->b, precord->nob * sizeof(double));
  memcpy(&trigger, (double *)precord->c, precord->noc * sizeof(double));
  memcpy(&offset, (double *)precord->d, precord->nod * sizeof(double));
 
  for(i=0; i< precord->noa; i++)
     {      
       if(arr[i]!=0){
         Npoints++;
       }
       zero[i]=0.0;
     }
  double *AxisArray;
  AxisArray = (double *) calloc (Npoints, sizeof(double));
 
  for (j=0; j<Npoints; j++)
    {
      AxisArray[j] = j * interval + offset*1000;
    }

  xtrig[0]=AxisArray[0];
  xtrig[1]=AxisArray[Npoints-1];
  ytrig[0]=trigger;
  ytrig[1]=trigger;
  
  //option 1
  memcpy((double *)precord->vala, zero, precord->nova * sizeof(double));
  //memcpy((double *)precord->vald, zero, precord->noa * sizeof(double));

  memcpy((double *)precord->vala, AxisArray, Npoints * sizeof(double));
  memcpy((double *)precord->valb, &xtrig, 2 * sizeof(double));
  memcpy((double *)precord->valc, &ytrig, 2 * sizeof(double));
  memcpy((long *)precord->vald,   &Npoints,  sizeof(long));

  //option 3
  //memset(precord->vala+Npoints,0,precord->noa-Npoints);
  free (AxisArray);
  return 0;
}
/* Register these symbols for use by IOC code: */


long my_asub_routineW(aSubRecord *precord)
{
  double arr[precord->noa];  //input parameter
  double zero[precord->noa];                        
  double interval;
  double trigger;
  double offset;

  //double AxisArray[precord->nova];  // output parameter 
  double xtrig[2],ytrig[2];         // trigger display
  //double WattsValues[precord->novd];// transformed measure watts
  
  int i,j;
  long Npoints=0;
 
  memcpy(&arr, (double *)precord->a, precord->noa * sizeof(double));
  memcpy(&interval, (double *)precord->b, precord->nob * sizeof(double));
  memcpy(&trigger, (double *)precord->c, precord->noc * sizeof(double));
  memcpy(&offset, (double *)precord->d, precord->nod * sizeof(double));
 
  for(i=0; i< precord->noa; i++)
     {      
       if(arr[i]!=0){
         Npoints++;
       }
       zero[i]=0.0;
     }
  double *AxisArray;
  AxisArray = (double *) calloc (Npoints, sizeof(double));
 
  for (j=0; j<Npoints; j++)
    {
      AxisArray[j] = j * interval + offset*1000;
    }

  xtrig[0]=AxisArray[0];
  xtrig[1]=AxisArray[Npoints-1];
  ytrig[0]=trigger;
  ytrig[1]=trigger;
  
  //option 1
  memcpy((double *)precord->vala, zero, precord->nova * sizeof(double));
  //memcpy((double *)precord->vald, zero, precord->noa * sizeof(double));
  //option 2 
  //memset(precord->vala,0,precord->nova);

  memcpy((double *)precord->vala, AxisArray, Npoints * sizeof(double));
  memcpy((double *)precord->valb, &xtrig, 2 * sizeof(double));
  memcpy((double *)precord->valc, &ytrig, 2 * sizeof(double));
  memcpy((long *)precord->vald,   &Npoints,  sizeof(long));

  //option 3
  //memset(precord->vala+Npoints,0,precord->noa-Npoints);
  free (AxisArray);
  return 0;
}
/* Register these symbols for use by IOC code: */

epicsRegisterFunction(my_asub_routineDBM);
epicsRegisterFunction(my_asub_routineW);

