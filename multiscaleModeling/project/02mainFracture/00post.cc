#include<stdio.h>
#include<string.h>
#include<iostream>
#include <cstdlib>
#include <iomanip>
#include <vector>
#include <unistd.h>
#include <cmath>
#include <time.h>

using namespace std;

int main()
{
	int n=40;
	
	
	int i,j,l,t;
	int dt=500;

	FILE *fp=NULL;
	fp=fopen("./post.txt","w+"); ///clear the contants.

	fclose(fp);		
	
	for (l=0;l<n;++l)
	{
		char s[10];
		char folder[100]="./postProcessing/singleGraph/";
		char file[100]="/line_T_p.xy";
		
		t=dt*(l+1);
		sprintf(s, "%d", t);
		strcat(folder,s);
		strcat(folder,file);
		
///////////////////////////		
printf("%s\n", folder);
///////////////////////////


		fp=fopen(folder,"r");

		int n_data=301;		// number of output data points	
		
		double data[301][3];  // !!!!!! '301' must equal n_data
	
		for (i=0;i<n_data; ++i)
		{
			for (j=0; j<3; ++j)
			{
			fscanf(fp, "%lf", &data[i][j]);
			}
		}


		fclose(fp);
		
///////////////////////////////////////////
printf("data[0][0] = %lf\n", data[0][0]);
printf("data[0][2] = %lf\n", data[0][2]);
printf("data[300][2] = %lf\n", data[300][2]);
///////////////////////////////////////////

		
		fp=fopen("./post.txt","a");

			fprintf(fp, "%.10g\n", data[300][1]);

		fclose(fp);
		
		
	}

	return 0;
}
