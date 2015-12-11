
/* Combine science frames into a composite "sky" image 		*/
/* Use object positions within the image to use only sky pixels */

#include "imageproc.h"

main(argc,argv)
	int argc;
	char *argv[];
{
	int	status=0,i,im,imnum,x,y,loc,xmin,xmax,ymin,ymax,num,delta;	
	void	printerror(),readimsections(),overscan();
	char	comment[FLEN_COMMENT],imagename[1000],command[1000],
		longcomment[1000],scaleregion[100],filter[200],oldfilter[200],
		obstype[200];
	float	avsigclip_sigma,*vecsort,
		*scaleval,*scalesort,maxval,
		val,sigmalim,mean;
	static desimage *data,datain,output,bias,bpm;
	/* define and initialize flags */
	int	flag_quiet=0,flag_combine=0,flag_bias=0,
		flag_variance=VARIANCE_DIRECT,flag_bpm=0,hdutype,
		flag_objreject=0,flag_growreject=0,growradius,
		flag_scale=1,scaleregionn[4]={500,1500,1500,2500},scalenum;
	void	rd_desimage(),shell(),decodesection();
	double	sumvariance,sumval,sum1,sum2;
	FILE	*inp,*pip;
	fitsfile *fptr;

	if (argc<4) {
	  printf("skycombine <input list> <output image> <options>\n");
	  printf("  -average\n");
	  printf("  -avsigclip <Sigma>\n");
	  printf("  -median (default)\n");
	  printf("  -growreject <pixel radius>\n");
	  /*printf("  -objectreject (expects object map in bit 4 of BPM)\n");*/
	  printf("  -scale <scale region>\n");
	  printf("  -noscale\n");
	  printf("  -variance <direct(default) or ccd>\n");
	  printf("  -novariance\n");
	  printf("  -quiet\n");
	  exit(0);
	}

	/* ******************************************* */
	/* ********  PROCESS COMMAND LINE ************ */
	/* ******************************************* */
	
	/* copy input image name if FITS file*/
	if (!strncmp(&(argv[1][strlen(argv[1])-5]),".fits",5))  {
	  printf("  flatcombine requires an input image list\n");
	  exit(0);
	}
	else { /* expect file containing list of flat images */
	  imnum=0;
	  inp=fopen(argv[1],"r");
	  while (fscanf(inp,"%s",imagename)!=EOF) {
	    imnum++;
	    if (strncmp(&(imagename[strlen(imagename)-5]),".fits",5)) {
	      printf("  ** File must contain list of FITS images **\n");
	      exit(0);
	    }
	    else { /* open file and check header */
	      if (fits_open_file(&fptr,imagename,READONLY,&status)) 
		printerror(status);
	      /* confirm OBSTYPE */
	      if (fits_read_key_str(fptr,"OBSTYPE",obstype,comment,&status)==
	      KEY_NO_EXIST) {
	        printf("  OBSTYPE keyword not found in %s \n",imagename);
		exit(0);
	      }
	      if (strncmp(obstype,"dome flat",9) && strncmp(obstype,"FLAT",4) &&
		strncmp(obstype,"flat",4) && strncmp(obstype,"object",6) &&
		strncmp(obstype,"OBJECT",6)) {
	        printf("  Expecting OBSTYPE 'dome flat', 'flat' or 'object' in %s\n",imagename);
		exit(0);
	      }
	      /* check filter */
	      if (fits_read_key_str(fptr,"FILTER",filter,comment,&status)==
	      KEY_NO_EXIST) {
	        printf("  FILTER keyword not found in %s \n",imagename);
		exit(0);
	      }
	      if (imnum==1) {
	        sprintf(oldfilter,"%s",filter);
		/*printf("  FILTER=%s\n",oldfilter);*/
	      }
	      else if (strcmp(filter,oldfilter)) {
	        printf("  Image %s is not taken in same filter %s\n",
		  imagename,filter);
		exit(0);
	      }
	      if (fits_close_file(fptr,&status)) printerror(status);
	    }
	  }
	  fclose(inp);
	  /* reopen file for processing */
	  inp=fopen(argv[1],"r");
	}
	
	/* prepare output file */
	sprintf(output.name,"!%s",argv[2]);
	if (strncmp(&(output.name[strlen(output.name)-5]),".fits",5)) {
	   printf("  ** Output file must be FITS image **\n");
	   exit(0);
	}

	/* set defaults */
	flag_combine=MEDIAN;
	/* process command line options */
	for (i=3;i<argc;i++) {
	  if (!strcmp(argv[i],"-quiet")) flag_quiet=1;
	  if (!strcmp(argv[i],"-objectreject")) flag_objreject=1; 
	  if (!strcmp(argv[i],"-growreject")) {
	    flag_growreject=1; 
	    i++;
	    sscanf(argv[i],"%d",&growradius);
	    if (growradius<1 || growradius>100) {
	      printf("  ** Grow radius must be between 1 and 100\n");
	      exit(0);
	    }
	  }
	  if (!strcmp(argv[i],"-noscale")) flag_scale=0; 
	  if (!strcmp(argv[i],"-scale")) {
	    flag_scale=1;
	    sprintf(scaleregion,"%s",argv[i+1]);
	    (scaleregion,scaleregionn,flag_quiet);
	  }
	  if (!strcmp(argv[i],"-average")) flag_combine=AVERAGE;
	  if (!strcmp(argv[i],"-median"))  flag_combine=MEDIAN;
	  if (!strcmp(argv[i],"-avsigclip")) {
	    flag_combine=AVSIGCLIP;
	    sscanf(argv[i+1],"%f",&avsigclip_sigma);
	  }
	  
	  if (!strcmp(argv[i],"-variance"))  {
	    if (i+i<argc) {
	     if (!strncmp(argv[i+1],"ccd",3)) flag_variance=VARIANCE_CCD;
	    }
	    else flag_variance=VARIANCE_DIRECT;
	  }
	  if (!strcmp(argv[i],"-novariance")) flag_variance=0;	
	    
	}	
	if (!flag_quiet) printf("  Input list %s contains %d FITS images\n",argv[1],imnum);
	
	
	
	/* ******************************************* */
	/* ******  REPORT PROCESSING PARAMETERS ****** */
	/* ******************************************* */
		
	if (!flag_quiet) {
	  if (flag_combine==AVERAGE) printf("  Averaging images\n");
	  else if (flag_combine==MEDIAN) {
	    printf("  Median combining images\n");
	  }
	  else if (flag_combine==AVSIGCLIP) {
	    printf("  Average sigma clipping with +/-%.1f sigma\n",avsigclip_sigma);
	    printf("  Not yet implemented\n");exit(0);
	  }
	}



	/* ******************************************* */
	/* ********  READ CALIBRATION IMAGES ********* */
	/* ******************************************* */
		
	/* read in and check bias image */
	if (flag_bias) {
	  if (!flag_quiet) printf("  Reading bias image %s\n",bias.name);
	  rd_desimage(&bias,READONLY,flag_quiet);
	  /* confirm that this is actual bias image */
	  /* make sure we are in the 1st extension */
	  if (fits_movabs_hdu(bias.fptr,1,&hdutype,&status)) printerror(status);
	  if (fits_read_keyword(bias.fptr,"DESZCMB",comment,comment,&status)==
	    KEY_NO_EXIST) {
	    printf("  ** BIAS image %s does not have DESZCMB keyword **\n",
	      bias.name);
	    exit(0);
	  }
	}
	
	/* read bad pixel mask image */
	if (flag_bpm) {
	  rd_desimage(&bpm,READONLY,flag_quiet);
	  /* confirm that this is actual bpm image */
	  if (fits_read_keyword(bpm.fptr,"DESBPM",comment,comment,&status)==
	    KEY_NO_EXIST) {
	    printf("  ** BPM image %s does not have DESBPM keyword **\n",
	      bpm.name);
	    status=0;
	  }
	}	




	/* ******************************************* */
	/* ********  READ and PROCESS RAW FLATS ****** */
	/* ******************************************* */


	/* create an array of image structures to hold the input images */
	data=(desimage *)calloc(imnum,sizeof(desimage));
	if (flag_combine==MEDIAN) vecsort=(float *)calloc(imnum,sizeof(float));
	if (flag_scale) { /* prepare for medianing the scale */
	  scalenum=(scaleregionn[1]-scaleregionn[0])*(scaleregionn[3]-scaleregionn[2]);
	  scalesort=(float *)calloc(scalenum,sizeof(float));
	}
	scaleval=(float *)calloc(imnum,sizeof(float));	
	
	/* now cycle through input images to read and prepare them */
	for (im=0;im<imnum;im++) {
	  /* get next image name */
	  fscanf(inp,"%s",datain.name);
	  if (!flag_quiet) printf("  Reading image %s\n",datain.name);
	  
	  /* read input image */
	  rd_desimage(&datain,READONLY,flag_quiet);
	  /* copy the name into the current image */
	  sprintf(data[im].name,"%s",datain.name);
	
	  /* retrieve basic image information from header */
	  if (fits_movabs_hdu(datain.fptr,1,&hdutype,&status)) printerror(status);
          /* get the BIASSEC information */          if (fits_read_key_str((datain.fptr),"BIASSECA",(datain.biasseca),comment,&status)
              ==KEY_NO_EXIST) {
            printf("  Keyword BIASSECA not defined in %s\n",datain.name);
            printerror(status);
          }
          if (!flag_quiet) printf("    BIASSECA = %s\n",(datain.biasseca));
          decodesection((datain.biasseca),(datain.biassecan),flag_quiet);

         /* get the AMPSEC information */
          if (fits_read_key_str(datain.fptr,"AMPSECA",datain.ampseca,comment,&status)
                ==KEY_NO_EXIST) {
            printf("  Keyword AMPSECA not defined in %s\n",datain.name);
            printerror(status);
          }
          if (!flag_quiet) printf("    AMPSECA  = %s\n",datain.ampseca);
          decodesection(datain.ampseca,datain.ampsecan,flag_quiet);

          /* get the BIASSEC information */
          if (fits_read_key_str(datain.fptr,"BIASSECB",datain.biassecb,comment,&status)
                ==KEY_NO_EXIST) {
            printf("  Keyword BIASSECB not defined in %s\n",datain.name);
            printerror(status);
          }
          if (!flag_quiet) printf("    BIASSECB = %s\n",datain.biassecb);
          decodesection(datain.biassecb,datain.biassecbn,flag_quiet);
          /* get the AMPSEC information */
          if (fits_read_key_str(datain.fptr,"AMPSECB",datain.ampsecb,comment,&status)
                ==KEY_NO_EXIST) {
            printf("  Keyword AMPSECB not defined in %s\n",datain.name);
            printerror(status);
          }
          if (!flag_quiet) printf("    AMPSECB  = %s\n",datain.ampsecb);
          decodesection(datain.ampsecb,datain.ampsecbn,flag_quiet);

          /* get the TRIMSEC information */
          if (fits_read_key_str(datain.fptr,"TRIMSEC",datain.trimsec,comment,&status)
                ==KEY_NO_EXIST) {
            printf("  Keyword TRIMSEC not defined in %s\n",datain.name);
            printerror(status);
          }
          if (!flag_quiet) printf("    TRIMSEC  = %s\n",datain.trimsec);
          decodesection(datain.trimsec,datain.trimsecn,flag_quiet);

          /* get the DATASEC information */
          if (fits_read_key_str(datain.fptr,"DATASEC",datain.datasec,comment,&status)
                ==KEY_NO_EXIST) {
            status=0;
            if (fits_read_key_str(datain.fptr,"CCDSEC",datain.datasec,comment,&status)
                ==KEY_NO_EXIST) {
              printf("  Keyword DATASEC and CCDSEC not defined in %s\n",
                datain.name);
              printerror(status);
            }
          }
          if (!flag_quiet) printf("    DATASEC  = %s\n",datain.datasec);
          decodesection(datain.datasec,datain.datasecn,flag_quiet);


	  /*readimsections(&datain,flag_quiet);	*/

	  /* confirm that filter is same as previous image */
	  if (im==0) { /* grab the filter name and keep it around */
	    if (fits_read_key_str(datain.fptr,"FILTER",oldfilter,comment,&status)==
	      KEY_NO_EXIST) {
	      printf("  ** FLAT image %s does not have FILTER keyword **\n",
	        datain.name);
	      exit(0);
	    }
	  }
	  else { /* make sure current image has same filter as first image */
	    if (fits_read_key_str(datain.fptr,"FILTER",filter,comment,&status)==
	      KEY_NO_EXIST) {
	      printf("  ** FLAT image %s does not have FILTER keyword **\n",
	        datain.name);
	      exit(0);
	    }
	    if (strcmp(filter,oldfilter)) {
	      printf("  **Image %s has wrong filter %s compared to filter %s of first image %s\n",
	        datain.name,filter,oldfilter,data[0].name);
	      exit(0);
	    }
	  }


	  /* ***** OVERSCAN Section ****** */
	  /* check to see if DESOSCN keyword is set */
	  if (fits_read_keyword(datain.fptr,"DESOSCN",comment,comment,&status)==KEY_NO_EXIST) {
	    if (!flag_quiet) printf("  Overscan correcting and trimming\n");
	    overscan(&datain,data+im,flag_quiet);
	    status=0;
	  }
	  else {/* image has already been OVERSCAN corrected and trimmed */
	    /* simply copy the data into the output array  */
	    data[im].bitpix=datain.bitpix;
	    data[im].npixels=datain.npixels;
	    data[im].nfound=datain.nfound;
	    for (i=0;i<datain.nfound;i++) data[im].axes[i]=datain.axes[i];
	    data[im].saturateA=datain.saturateA;data[im].saturateB=datain.saturateB;
	    data[im].gainA=datain.gainA;data[im].gainB=datain.gainB;
	    data[im].rdnoiseA=datain.rdnoiseA;data[im].rdnoiseB=datain.rdnoiseB;
	    data[im].image=(float *)calloc(data[im].npixels,sizeof(float));
	    for (i=0;i<data[im].npixels;i++) data[im].image[i]=datain.image[i];

	  }
	  
 	  /* need to make sure bias and bpm are same size as flat image */
	  for (i=0;i<output.nfound;i++) {
	    if (data[im].axes[i]!=bpm.axes[i] && flag_bpm) {
	      printf("   %s (%dX%d) different size than flat image %s (%dX%d)\n",
	        bpm.name,bpm.axes[0],bpm.axes[1],data[im].name,data[im].axes[0],
		data[im].axes[1]);
	      exit(0);
	    }
	    if (data[im].axes[i]!=bias.axes[i] && flag_bias) {
	      printf("  BIAS image %s (%dX%d) different size than flat image %s (%dX%d)\n",
	        bias.name,bias.axes[0],bias.axes[1],data[im].name,data[im].axes[0],
		data[im].axes[1]);
	      exit(0);
	    }
	  }

	  
	  /* ***** BIAS Section ****** */
	  /* check to see if DESBIAS keyword is set */
	  if (fits_read_keyword(datain.fptr,"DESBIAS",comment,comment,&status)==KEY_NO_EXIST) {
	    if (!flag_quiet) printf("  Bias subtracting\n");
	    status=0;
	    /* only bias subtract the non-flagged pixels if using bpm */
	    if (flag_bpm) for (i=0;i<data[im].npixels;i++) 
	      if (!bpm.mask[i]) data[im].image[i]-=bias.image[i];
	    /* otherwise bias subtract all pixels */
	    else for (i=0;i<data[im].npixels;i++) data[im].image[i]-=bias.image[i];
	  }
	  
	  /* should scan for saturated pixels and complain if the number is large */
	  
	  /* calculate the scale in the scaleregion */
	  if (flag_scale) {
	    i=0;
	    for (y=scaleregionn[2]-1;y<scaleregionn[3]-1;y++) 
	      for (x=scaleregionn[0]-1;x<scaleregionn[1]-1;x++) {
	        loc=x+y*data[im].axes[0];
	        if (loc>=0 && loc<data[im].npixels) {
		  if ((flag_bpm && !bpm.mask[loc]) || !flag_bpm) {
	            scalesort[i]=data[im].image[loc];
	            i++;
		  }
		}
	      }
	    if (!flag_quiet) 
	      printf("  Region size used to scale image %s is %d pixels\n",
	      data[im].name,i);
	    if (i<100) {
	      printf("  **Useable scale region withn [%d:%d,%d:%d] too small for %s\n",
	      scaleregionn[0],scaleregionn[1],scaleregionn[2],scaleregionn[3],data[im].name);
	    }
	    /* sort list */
	    shell(i,scalesort-1);
	    /* grab the median */
	    if (i%2) scaleval[im]=scalesort[i/2];
	    else scaleval[im]=0.5*(scalesort[i/2]+scalesort[i/2-1]);
	    if (!flag_quiet) printf("  Scale value in region [%d:%d,%d:%d] is %.1f\n",
	      scaleregionn[0],scaleregionn[1],scaleregionn[2],scaleregionn[3],
	      scaleval[im]);
	  }
	  else scaleval[im]=1.0;
	  		  
	  if (im==0) { /* prepare output image first time through*/
	    output=data[im];
	    for (i=0;i<output.nfound;i++) output.axes[i]=data[im].axes[i];
	    output.bitpix=FLOAT_IMG;
	    output.npixels=data[im].npixels;
	    sprintf(output.name,"!%s",argv[2]);
	    output.image=(float *)calloc(output.npixels,sizeof(float));
	    if (flag_variance) {
	      /* prepares variance image */
	      output.varim=(float *)calloc(output.npixels,sizeof(float));
	    }
	  }
	  /* close input FITS file before moving on */
	  if (fits_close_file(datain.fptr,&status)) printerror(status);
	  free(datain.image);
	}  /* all the input images have been read and overscan+bias subtracted */

	/* close input file list */	
	fclose(inp);
	if (!flag_quiet) printf("  Closed image list %s\n",argv[1]);

	
	/* ******************************************* */
	/* *********  COMBINE SECTION *************** */
	/* ******************************************* */
	
	if (!flag_quiet) printf("  Combining images \n");
	maxval=0.0;  /* reset maxval */
	/* Combine the input images to create composite */
	if (flag_combine==AVERAGE) {
  	  for (i=0;i<output.npixels;i++) {
	    output.image[i]=0;
	    if ((!bpm.mask[i] && flag_bpm) || !flag_bpm) {
	      for (im=0;im<imnum;im++) output.image[i]+=(data[im].image[i]/scaleval[im]);
	      output.image[i]/=(float)imnum;
	    }
	  }
	}
	
	if (flag_combine==MEDIAN) {
  	  for (i=0;i<output.npixels;i++) { /* for each pixel */
	    output.image[i]=0;
	    if ((!bpm.mask[i] && flag_bpm) || !flag_bpm) {
	      /* copy values into sorting vector */
	      for (im=0;im<imnum;im++) vecsort[im]=data[im].image[i]/scaleval[im];
	      shell(imnum,vecsort-1);
	      /* odd number of images */
	      if (imnum%2) output.image[i]=vecsort[imnum/2]; /* record the median value */  
	      else output.image[i]=0.5*(vecsort[imnum/2]+vecsort[imnum/2-1]);
	    }
	  }
	}

	if (flag_combine==AVSIGCLIP) {
	  printf("  Not yet implemented\n"); exit(0);
	}
	
	/* now let's confirm the final scaling */
	if (flag_scale) {
	i=0;
	for (y=scaleregionn[2]-1;y<scaleregionn[3]-1;y++) 
	  for (x=scaleregionn[0]-1;x<scaleregionn[1]-1;x++) {
	    loc=x+y*output.axes[0];
	    if (loc>=0 && loc<output.npixels) {
	      if ((flag_bpm && !bpm.mask[loc]) || !flag_bpm) {
	        scalesort[i]=output.image[loc];
	        i++;
	      }
	    }
	}
	if (!flag_quiet) 
	  printf("  Region size used to scale image %s is %d pixels\n",
	    output.name+1,i);
	if (i<100) {
	  printf("  **Useable scale region withn [%d:%d,%d:%d] too small for %s\n",
	  scaleregionn[0],scaleregionn[1],scaleregionn[2],scaleregionn[3],output.name);
	}  
	shell(i,scalesort-1);
	if (i%2) maxval=scalesort[i/2];
	else maxval=0.5*(scalesort[i/2]+scalesort[i/2-1]);
	
	if (!flag_quiet) {
	  printf("  Scale value of output image in region [%d:%d,%d:%d] is %.5f\n",
	    scaleregionn[0],scaleregionn[1],scaleregionn[2],scaleregionn[3],
	    maxval);
	  printf("  Rescaling to 1.0\n");
	}
	/* cycle through resulting image to normalize it to 1.0 */
	for (i=0;i<output.npixels;i++) output.image[i]/=maxval;
	}
	
	
	
	
	/* ******************************************* */
	/* *********  VARIANCE SECTION *************** */
	/* ******************************************* */
	
	if (flag_variance==VARIANCE_DIRECT) { /* now prepare direct variance image for the flat field */
	  if (!flag_quiet) printf("  Beginning direct variance calculation\n");
	  /* first estimate two variances to use for sigma clipping */
	  /* use hardwired central region of the chip */
	  sum2=sum1=0.0;num=0;
	  for (y=1500;y<2500;y++) for (x=800;x<1200;x++) {
	    loc=y*output.axes[0]+x;
	    for (im=0;im<imnum;im++) {
	      if ((flag_bpm && !bpm.mask[loc]) || !flag_bpm) {
	      	 val=data[im].image[loc]/scaleval[im]/maxval-output.image[loc]; 
	         sum2+=Squ(val);sum1+=val;
	         num++;
	      }
	    }
	  }
	  mean=sum1/(float)num;
	  sigmalim=3.5*sqrt(sum2/(float)num-Squ(mean));
	  if (!flag_quiet) printf("  Estimated variance and mean for composite flat is %.5f/%.5f\n",
	    sigmalim/3.5,mean);
	  delta=VARIANCE_DELTAPIXEL;
	  
	  
	  if (!flag_quiet) printf("  Now calculating pixel by pixel variance using %dX%d square centered on each pixel\n",
	    2*delta+1,2*delta+1);
	  for (i=0;i<output.npixels;i++) {
	   if ((flag_bpm && !bpm.mask[i]) || !flag_bpm) {
	    x=i%output.axes[0];y=i/output.axes[0];
	    /* define a small square centered on this pixel */
	    
	    xmin=x-delta;xmax=x+delta;
	      if (xmin<0) {xmax+=abs(xmin);xmin=0;} /* hanging off bottom edge? */
	      if (xmax>=output.axes[0]) /* hanging off top edge? */
	        {xmin-=(xmax-output.axes[0]+1);xmax=output.axes[0]-1;}    
	    
	    ymin=y-delta;ymax=y+delta;
	      if (ymin<0) {ymax+=abs(ymin);ymin=0;} /* hanging off bottom edge? */
	      if (ymax>=output.axes[1])  /* hanging off top edge? */
	        {ymin-=(ymax-output.axes[1]+1);ymax=output.axes[1]-1;}

	    sum2=sum1=0.0;num=0;	    
	    for (x=xmin;x<=xmax;x++) for (y=ymin;y<=ymax;y++) {
	    loc=x+y*output.axes[0];  
	      for (im=0;im<imnum;im++) {
	        val=data[im].image[loc]/scaleval[im]/maxval-output.image[loc]; 
	        if (fabs(val)<sigmalim && ((flag_bpm && !bpm.mask[loc]) || !flag_bpm)) {
	          sum2+=Squ(val);
		  sum1+=val;
		  num++;
	        }
	      }
	    }
	    if (num>1) {
	      mean=sum1/(float)num;
	      val=(sum2/(float)num-Squ(mean))/(float)imnum;
	    }
	    else {
	      printf("  *** Warning:  No pixels meet criterion for inclusion\n");
	      val=sigmalim/3.5/(float)imnum; 
	    }
	    output.varim[i]=1.0/val;
	   }
	   else output.varim[i]=0.0;
	  }
	} /* end of VARIANCE_DIRECT section */	
	else if (flag_variance==VARIANCE_CCD) {
	  if (!flag_quiet) printf("  Beginning CCD statical variance calculation\n");
	  for (i=0;i<output.npixels;i++) 
	    if ((flag_bpm && !bpm.mask[i]) || !flag_bpm) {
	      sumval=sumvariance=0.0;
	      for (im=0;im<imnum;im++) {
	        if (i%output.axes[0]<1024) { /* in AMP A section */	      
		  /* each image contributes Poisson noise, RdNoise and BIAS image noise */
	          sumval=(data[im].image[i]/data[im].gainA+
		    Squ(data[im].rdnoiseA/data[im].gainA)+1.0/bias.varim[i])/Squ(scaleval[im]);
		}
		else { /* in AMP B */
		  /* each image contributes Poisson noise, RdNoise and BIAS image noise */
	          sumval=(data[im].image[i]/data[im].gainB+
		    Squ(data[im].rdnoiseB/data[im].gainB)+1.0/bias.varim[i])/Squ(scaleval[im]);		
		}
		sumvariance+=(sumval/Squ(maxval));
	      }
	      output.varim[i]=Squ((float)imnum)/sumvariance;	
	    }
	    else output.varim[i]=0.0;
	} /* end of VARIANCE_CCD section */
		
	/* **** SAVE RESULTS ***** */
	printf("  Writing results to %s",output.name+1);
	/* create the file */
        if (fits_create_file(&output.fptr,output.name,&status)) 
	  printerror(status);

	/* create image extension */
	if (fits_create_img(output.fptr,FLOAT_IMG,2,output.axes,&status)) printerror(status);
	/* write the corrected image*/
	if (fits_write_img(output.fptr,TFLOAT,1,output.npixels,output.image,&status))
	  printerror(status);
	  
	/* write basic information into the header */
	if (fits_write_key_str(output.fptr,"OBSTYPE","dome flat","Observation type",&status))
	  printerror(status);  
	if (fits_write_key_str(output.fptr,"FILTER",oldfilter,"Filter name(s)",&status))
	  printerror(status);
	/* Write information into the header describing the processing */
	pip=popen("date","r");
	fgets(comment,200,pip);
	comment[strlen(comment)-1]=0;
	pclose(pip);
	if (fits_write_key_str(output.fptr,"DESFCMB",comment,"flatcombine output",&status))
	  printerror(status);
	sprintf(longcomment,"DESDM:");
	for (i=0;i<argc;i++) sprintf(longcomment,"%s %s",longcomment,argv[i]);
	if (!flag_quiet) printf("\n  %s\n", longcomment);
	if (fits_write_comment(output.fptr,longcomment,&status)) printerror(status);
	sprintf(longcomment,"DESDM: (%d) ",imnum);
	for (im=0;im<imnum;im++) sprintf(longcomment,"%s %s ",longcomment,data[im].name);
	if (!flag_quiet) printf("  %s\n", longcomment);
	if (fits_write_comment(output.fptr,longcomment,&status)) printerror(status);
	if (fits_write_key_str(output.fptr,"DES_EXT","IMAGE","Image extension",
	  &status)) printerror(status);

	if (flag_variance) {
	  /* now store the variance image that has been created or updated */
	  /* first create a new extension */
	  if (fits_create_img(output.fptr,FLOAT_IMG,2,output.axes,&status))
	    printerror(status);
	  /* write the data */	  
	  if (fits_write_img(output.fptr,TFLOAT,1,output.npixels,output.varim,
	    &status)) printerror(status);
	  if (fits_write_key_str(output.fptr,"DES_EXT","VARIANCE","Extension type",&status)) 
	    printerror(status);
	}


        /* close the corrected image */
        if (fits_close_file(output.fptr,&status)) printerror(status);

	printf("\n");
	
	free(output.image);
	for (im=0;im<imnum;im++) free(data[im].image);
	if (flag_bias) {
	  free(bias.image);
	  if (bias.varim!=NULL) free(bias.varim);
	}
	if (flag_bpm) free(bpm.mask);

	return(0);
}