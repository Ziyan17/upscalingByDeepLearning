#include<stdio.h>
#include<string.h>
#include<iostream>
#include <cstdlib>
#include <iomanip>
#include <vector>
#include <unistd.h>
#include <cmath>

using namespace std;
int nx=500,ny=10, nxTilted = 10, nyTilted = 100, nxMicro = 10, nyMicro = 300;  // grid number
double lz=2;

int i,j;


double pi = 3.14159265358979323846;
double theta = 3.14159265358979323846 / 180.0 *75.0; // angle between horizontal and vertical fractures
double l = 51.45322617, r = 7.5; // l is the length of the horizontal fracture, r is the distance between horizontal fractures; l is overwitten later to match the grid position.
double a1 = 0.1, a2 = 0.2, b1 = 0.2, b2 = 0.1; //0.1, 0.2, 0.2, 0.1, which are HALF APERTURE of main fractures

// micro fracture info
double b0 = 0.005, d = 0.1; // HALF APERTURE of microfractures and distance between microfractures. Note that d is overwitten later to match the grid position.
double x;

double dx; // grid size for the horizontal fracture
double xc1, xc2, xc3; // x coordinates of crossings

int number = 13; // number of the fractures
int initialNumber = 13; // number of the main fractures

FILE *fp=NULL;

// helper function: compute the vertices of horizontal fractures
void verticesHorizontal(double x1, double y1, double a, double bb1, double bb2, FILE *fp) {
	
	fprintf(fp, "(%.10g %.10g %.10g)\n", - bb1/sin(theta) - a/tan(theta) + x1, - a + y1, -lz/2);
	fprintf(fp, "(%.10g %.10g %.10g)\n", bb2/sin(theta) - a/tan(theta) + x1 + l, - a + y1, -lz/2);
	fprintf(fp, "(%.10g %.10g %.10g)\n", bb2/sin(theta) + a/tan(theta) + x1 + l, a + y1, -lz/2);
	fprintf(fp, "(%.10g %.10g %.10g)\n", - b1/sin(theta) + a/tan(theta) + x1, a + y1, -lz/2);
		
	fprintf(fp, "(%.10g %.10g %.10g)\n", - bb1/sin(theta) - a/tan(theta) + x1, - a + y1, lz/2);
	fprintf(fp, "(%.10g %.10g %.10g)\n", bb2/sin(theta) - a/tan(theta) + x1 + l, - a + y1, lz/2);
	fprintf(fp, "(%.10g %.10g %.10g)\n", bb2/sin(theta) + a/tan(theta) + x1 + l, a + y1, lz/2);
	fprintf(fp, "(%.10g %.10g %.10g)\n", - bb1/sin(theta) + a/tan(theta) + x1, a + y1, lz/2);

	return;
}

// helper function: compute the vertices of vertical fractures
void verticesTilted(double x1, double y1, double aa1, double aa2, double b, FILE *fp) {
	
	fprintf(fp, "(%.10g %.10g %.10g)\n", - b/sin(theta) + aa1/tan(theta) + x1, aa1 + y1, -lz/2);
	fprintf(fp, "(%.10g %.10g %.10g)\n", b/sin(theta) + aa1/tan(theta) + x1, aa1 + y1, -lz/2);
	fprintf(fp, "(%.10g %.10g %.10g)\n", b/sin(theta) - aa2/tan(theta) + x1 + r/tan(theta), - aa2 + y1 + r, -lz/2);
	fprintf(fp, "(%.10g %.10g %.10g)\n", - b/sin(theta) - aa2/tan(theta) + x1 + r/tan(theta), - aa2 + y1 + r, -lz/2);
		
	fprintf(fp, "(%.10g %.10g %.10g)\n", - b/sin(theta) + aa1/tan(theta) + x1, aa1 + y1, lz/2);
	fprintf(fp, "(%.10g %.10g %.10g)\n", b/sin(theta) + aa1/tan(theta) + x1, aa1 + y1, lz/2);
	fprintf(fp, "(%.10g %.10g %.10g)\n", b/sin(theta) - aa2/tan(theta) + x1 + r/tan(theta), - aa2 + y1 + r, lz/2);
	fprintf(fp, "(%.10g %.10g %.10g)\n", - b/sin(theta) - aa2/tan(theta) + x1 + r/tan(theta), - aa2 + y1 + r, lz/2);	
	return;
}

	

int main()
{
	fp=fopen("./system/blockMeshDict","a");
	
//// Step 0: calculate parameters
	dx = d / sin(theta);
	l = dx * nx - b1/sin(theta) - b2/sin(theta);
	xc1 = dx * 100 - b1/sin(theta) - b2/sin(theta);
	xc2 = dx * 300 - b1/sin(theta) - b1/sin(theta);
	xc3 = dx * 400 - b1/sin(theta) - b2/sin(theta);
	
	
//// Step 1: define the vertices
	
	fprintf(fp, "vertices\n");
	fprintf(fp, "(\n");
	// Step 1.1: vertices for hydraulic fracture
		// bottom one
		verticesHorizontal(0.0, 0.0, a1, b1 ,b2, fp);
		
		// middle one (wide)
		verticesHorizontal(r/tan(theta), r, a2, b1 ,b2, fp);

		// upper one
		verticesHorizontal(2.0 * r/tan(theta), 2.0 * r, a1, b1 ,b2, fp);	
		
		// bottom left 1 (wide)
		verticesTilted(0.0, 0.0, a1, a2, b1, fp);

		// upper left 1 (wide)	
		verticesTilted(r/tan(theta), r, a2, a1, b1, fp);
		
		// bottom left 2
		verticesTilted(xc1, 0.0, a1, a2, b2, fp);
		
		// upper left 2
		verticesTilted(xc1 + r/tan(theta), r, a2, a1, b2, fp);
		
		// bottom left 3 (wide)
		verticesTilted(xc2, 0.0, a1, a2, b1, fp);

		// upper left 3 (wide)	
		verticesTilted(xc2 + r/tan(theta), r, a2, a1, b1, fp);
		
		// bottom left 4
		verticesTilted(xc3, 0.0, a1, a2, b2, fp);
		
		// upper left 4
		verticesTilted(xc3 + r/tan(theta), r, a2, a1, b2, fp);		
		
		// bottom left 5
		verticesTilted(l, 0.0, a1, a2, b2, fp);
		
		// upper left 5
		verticesTilted(l + r/tan(theta), r, a2, a1, b2, fp);	
		
	// Step 1.2: vertices for micro fractures

	
	fprintf(fp, ");\n\n");
	
//// Step 2: define the blocks
	fprintf(fp, "blocks\n");
	fprintf(fp, "(\n");	
	for (i=0;i<3;++i)
	{
		fprintf(fp, "hex (%d %d %d %d %d %d %d %d) (%d %d %d) simpleGrading (1 1 1)\n",8*i+0,8*i+1,8*i+2,8*i+3,8*i+4,8*i+5,8*i+6,8*i+7,nx,ny,1);	
	}
	for (i=3;i<initialNumber;++i)
	{
		fprintf(fp, "hex (%d %d %d %d %d %d %d %d) (%d %d %d) simpleGrading (1 1 1)\n",8*i+0,8*i+1,8*i+2,8*i+3,8*i+4,8*i+5,8*i+6,8*i+7,nxTilted, nyTilted, 1);	
	}
	for (i=initialNumber;i<number;++i)
	{
		fprintf(fp, "hex (%d %d %d %d %d %d %d %d) (%d %d %d) simpleGrading (1 1 1)\n",8*i+0,8*i+1,8*i+2,8*i+3,8*i+4,8*i+5,8*i+6,8*i+7,nxMicro, nyMicro, 1);	
	}	
	fprintf(fp, ");\n\n");

	fprintf(fp, "edges\n(\n);\n\n");
//// Step 2: define the boundaries	

	fprintf(fp, "boundary\n(\n");
//// Step 2.1: leakyWall
	fprintf(fp, "leakyWallA\n{\ntype wall;\nfaces\n(\n");
	fprintf(fp, "(%d %d %d %d)\n", 3, 7, 6, 2);
	fprintf(fp,");\n}\n\n");	




	fprintf(fp, "leakyWallB\n{\ntype wall;\nfaces\n(\n");
	fprintf(fp, "(%d %d %d %d)\n", 9, 13, 12, 8);
	fprintf(fp,");\n}\n\n");



	fprintf(fp, "leakyWallC\n{\ntype wall;\nfaces\n(\n");
	fprintf(fp, "(%d %d %d %d)\n", 11, 15, 14, 10);		
	fprintf(fp,");\n}\n\n");
	

	
	fprintf(fp, "leakyWallD\n{\ntype wall;\nfaces\n(\n");
	fprintf(fp, "(%d %d %d %d)\n", 17, 21, 20, 16);	
	fprintf(fp,");\n}\n\n");	
//// Step 2.2: deadWall	
	
	fprintf(fp, "deadWall\n{\ntype wall;\nfaces\n(\n");
	
	fprintf(fp, "(%d %d %d %d)\n", 1, 5, 4, 0);
	/// middle
	fprintf(fp, "(%d %d %d %d)\n", 0, 4, 7, 3);
	
	fprintf(fp, "(%d %d %d %d)\n", 2, 6, 5, 1);
	
	// fprintf(fp, "(%d %d %d %d)\n", 8, 12, 15, 11);
	// fprintf(fp, "(%d %d %d %d)\n", 10, 14, 13, 9);
	
	fprintf(fp, "(%d %d %d %d)\n", 16, 20, 23, 19);
	fprintf(fp, "(%d %d %d %d)\n", 19, 23, 22, 18);
	// middle
	fprintf(fp, "(%d %d %d %d)\n", 18, 22, 21, 17);
	
	///////////////////////////////////////////////////////

	for (i=3; i<initialNumber; ++i)
	{
		fprintf(fp, "(%d %d %d %d)\n", 8*i+0, 8*i+4 , 8*i+7 , 8*i+3);
		fprintf(fp, "(%d %d %d %d)\n", 8*i+2, 8*i+6 , 8*i+5 , 8*i+1);
	}
		
	fprintf(fp,");\n}\n\n");
//// Step 2.2: sidewalls


//// Step 2.3: interfaces

	fprintf(fp, "interfaceA\n{\ntype patch;\nfaces\n(\n");

	for (i=3; i<number; i=i+2)
	{
		fprintf(fp, "(%d %d %d %d)\n", 8*i+1, 8*i+5 , 8*i+4 , 8*i+0);
	}	
	fprintf(fp,");\n}\n\n");	


	fprintf(fp, "interfaceB\n{\ntype patch;\nfaces\n(\n");
	for (i=3; i<number; i=i+2)
	{
		fprintf(fp, "(%d %d %d %d)\n", 8*i+3, 8*i+7 , 8*i+6 , 8*i+2);
	}	
	fprintf(fp,");\n}\n\n");
	
	
	
	fprintf(fp, "interfaceC\n{\ntype patch;\nfaces\n(\n");
	for (i=4; i<number; i=i+2)
	{
		fprintf(fp, "(%d %d %d %d)\n", 8*i+1, 8*i+5 , 8*i+4 , 8*i+0);
	}	
	fprintf(fp,");\n}\n\n");		



	fprintf(fp, "interfaceD\n{\ntype patch;\nfaces\n(\n");
	for (i=4; i<number; i=i+2)
	{
		fprintf(fp, "(%d %d %d %d)\n", 8*i+3, 8*i+7 , 8*i+6 , 8*i+2);
	}	
	fprintf(fp,");\n}\n\n");
	
	
//// Step 2.4: inlet
	fprintf(fp, "inlet\n{\ntype patch;\nfaces\n(\n(8 12 15 11)\n);\n}\n\n");
//// Step 2.5: outlet

	fprintf(fp, "outlet\n{\ntype patch;\nfaces\n(\n");
	
	fprintf(fp, "(%d %d %d %d)\n", 10, 14, 13, 9);
	
	fprintf(fp,");\n}\n\n");
	
	
//// Step 2.6: front and back walls


	fprintf(fp, "frontAndBack\n{\ntype empty;\nfaces\n(\n");
	for (i=0; i<number; ++i)
	{
		fprintf(fp, "(%d %d %d %d)\n", 8*i+0, 8*i+3 , 8*i+2 , 8*i+1);
		fprintf(fp, "(%d %d %d %d)\n", 8*i+4, 8*i+5 , 8*i+6 , 8*i+7);
	}	
	
	fprintf(fp,");\n}\n\n");
///////////////////////////////
	fprintf(fp,");\n\n");	

//// Step 3: Merge boundary

	fprintf(fp, "mergePatchPairs\n(\n");
	fprintf(fp, "(leakyWallA interfaceA)\n");
	fprintf(fp, "(leakyWallB interfaceB)\n");
	fprintf(fp, "(leakyWallC interfaceC)\n");
	fprintf(fp, "(leakyWallD interfaceD)\n");
	fprintf(fp, ");\n");
	fclose(fp);


	return 0;
}


	
