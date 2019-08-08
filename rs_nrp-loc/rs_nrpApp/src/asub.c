#include <registryFunction.h>
#include <aSubRecord.h>
#include <epicsExport.h>


static long my_asub_routine(aSubRecord *precord)
{
  long *data;
  data = (long *) precord->a;
  memcpy(precord->vala, data, sizeof(long));
  return 0;
}
/* Register these symbols for use by IOC code: */

epicsRegisterFunction(my_asub_routine);

