===================
Data Pre-Processing
===================

.. |br| raw:: html

   <br />

.. warning::
   The documentation is under active development.
   Statistical and machine learning models will be made available once fully
   validated.

--------------------
MUSE/RAVENS Pipeline
--------------------

The MUSE/RAVENS pipeline performs the anatomical segmentation and parcellation.
Following these steps will setup the MUSE/RAVENS processing pipeline using a
singularity container.

^^^^^
Setup
^^^^^

Running the scripts inside the container requires Git and Singularity.
Follow directions of the respective tools to install Singularity
(https://sylabs.io/guides/3.8/admin-guide/installation.html) and Git
(https://github.com/git-guides/install-git).

Make sure that the commands `singularity` and `git` are available in the
terminal, for instance by adding them to the `$PATH` environment variable.

Additionally, make sure that an environment variable `$TMPDIR` points to a
temporary scratch space that can be used to store intermediate results.
Otherwise, it will be set to `$PWD` (i.e. the current working directory).

^^^^^^^^^^^^^^^^
Complete example
^^^^^^^^^^^^^^^^

1. Clone the istaging git repository

.. code-block:: shell

   GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/CBICA/NiBAx/
   cd NiBAx/Image_Processing/sMRI
   git lfs pull --include example
   git lfs pull --include sMRI_ProcessingPipeline


2. Download from the singularity cloud and save the .sif file in the `Container/` folder.

.. code-block:: shell

   cd Container
   singularity pull library://jimitdoshi/cbica/cbica-muse-pipeline:1.0.0 
   cd ..


3. Follow the example provided in the `example/` directory

.. code-block:: shell

   bash example/run_example.sh


4. This step will create a `Protocols` directory inside `example` which contains all the results files.

.. code-block:: shell

	 # Re-orientation to LPS
	 example/Protocols/ReOrientedLPS/SUB-01/SUB-01_T1_LPS.nii.gz

	 # Intensity inhomogeneity correction
	 example/Protocols/BiasCorrected/SUB-01/SUB-01_T1_LPS_N4.nii.gz

	 # Brain extraction	
	 example/Protocols/Skull-Stripped/SUB-01/SUB-01_T1_LPS_N4_brainmask_muse-ss.nii.gz
	 example/Protocols/Skull-Stripped/SUB-01/SUB-01_T1_LPS_N4_brain_muse-ss.nii.gz
	 example/Protocols/Skull-Stripped/SUB-01/SUB-01_T1_LPS_N4_ROI_1_SimRank.nii.gz
 
	 # Another round of inhomogeneity correction using fast
	 example/Protocols/fastbc/SUB-01/SUB-01_T1_LPS_N4_brain_muse-ss_fastbc_seg.nii.gz
	 example/Protocols/fastbc/SUB-01/SUB-01_T1_LPS_N4_brain_muse-ss_fastbc.nii.gz  

	 # MUSE ROI labeling
	 example/Protocols/MUSE/SUB-01/SUB-01_T1_LPS_N4_brain_muse-ss_fastbc_muse.nii.gz
	 example/Protocols/MUSE/SUB-01/SUB-01_T1_LPS_N4_brain_muse-ss_fastbc_muse_DerivedVolumes.csv

	 # Tissue segmentation using MUSE ROIs
	 example/Protocols/Segmented/SUB-01/SUB-01_T1_LPS_N4_brain_muse-ss_fastbc_muse_seg.nii.gz

	 # RAVENS
	 example/Protocols/RAVENS/SUB-01/SUB-01_T1_LPS_N4_brain_muse-ss_fastbc_rTemplate_ants-0.5_JacDet.nii.gz
	 example/Protocols/RAVENS/SUB-01/SUB-01_T1_LPS_N4_brain_muse-ss_fastbc_rTemplate_ants-0.5.nii.gz
	 example/Protocols/RAVENS/SUB-01/SUB-01_T1_LPS_N4_brain_muse-ss_fastbc_muse_seg_ants-0.5_RAVENS_10.nii.gz
	 example/Protocols/RAVENS/SUB-01/SUB-01_T1_LPS_N4_brain_muse-ss_fastbc_muse_seg_ants-0.5_RAVENS_50.nii.gz
	 example/Protocols/RAVENS/SUB-01/SUB-01_T1_LPS_N4_brain_muse-ss_fastbc_muse_seg_ants-0.5_RAVENS_150.nii.gz
	 example/Protocols/RAVENS/SUB-01/SUB-01_T1_LPS_N4_brain_muse-ss_fastbc_muse_seg_ants-0.5_RAVENS_250.nii.gz

	 # Post-processed RAVENS
	 ### Smoothed by 2mm
	 example/Protocols/RAVENS/SUB-01/SUB-01_T1_LPS_N4_brain_muse-ss_fastbc_muse_seg_ants-0.5_RAVENS_10_s2.nii.gz
	 example/Protocols/RAVENS/SUB-01/SUB-01_T1_LPS_N4_brain_muse-ss_fastbc_muse_seg_ants-0.5_RAVENS_50_s2.nii.gz
	 example/Protocols/RAVENS/SUB-01/SUB-01_T1_LPS_N4_brain_muse-ss_fastbc_muse_seg_ants-0.5_RAVENS_150_s2.nii.gz
	 example/Protocols/RAVENS/SUB-01/SUB-01_T1_LPS_N4_brain_muse-ss_fastbc_muse_seg_ants-0.5_RAVENS_250_s2.nii.gz
	 ### Downsampled to 2mmx2mmx2mm
	 example/Protocols/RAVENS/SUB-01/SUB-01_T1_LPS_N4_brain_muse-ss_fastbc_muse_seg_ants-0.5_RAVENS_10_s2_DS.nii.gz
	 example/Protocols/RAVENS/SUB-01/SUB-01_T1_LPS_N4_brain_muse-ss_fastbc_muse_seg_ants-0.5_RAVENS_50_s2_DS.nii.gz
	 example/Protocols/RAVENS/SUB-01/SUB-01_T1_LPS_N4_brain_muse-ss_fastbc_muse_seg_ants-0.5_RAVENS_150_s2_DS.nii.gz
	 example/Protocols/RAVENS/SUB-01/SUB-01_T1_LPS_N4_brain_muse-ss_fastbc_muse_seg_ants-0.5_RAVENS_250_s2_DS.nii.gz

---------------
fMRI Processing
---------------

This pipeline is for pre-processing fMRI time-series using an incrementally
modified version of the [UK_biobank_pipeline](https://git.fmrib.ox.ac.uk/falmagro/UK_biobank_pipeline_v_1). 
The pipeline removes structured artifacts using ICA+FIX [2], resamples filtered functional data to standard space, applies GIGICA [3] on functional data to extract features. Higher level functionalities include:

 i) Generating filtered functional data and resampling to standard space(MNI152_2mm)  
 ii) Getting subject specific IC time courses using GIGICA.  
 iii) Getting Correlation Matrices at two different dimensionalities 25(21 useful components) and 100(55 useful)


^^^^^^^^^^^^^^^^^
Packages required
^^^^^^^^^^^^^^^^^

UKBiobank pipeline (https://github.com/CBICA/UK_biobank_pipeline_v_1.git)  

GIGICA - Group Information Guided ICA (https://www.nitrc.org/projects/gig-ica/)

FSL and AFNI

^^^^^^^
Outputs
^^^^^^^

Dimensions : n = 25 or 100 components (Group ICs from UKBiobank)  |br|
Good Components list are in : (only useful components are extracted and saved)  |br|
n25 :  https://www.fmrib.ox.ac.uk/ukbiobank/group_means/rfMRI_GoodComponents_d25_v1.txt |br|
n100 : https://www.fmrib.ox.ac.uk/ukbiobank/group_means/rfMRI_GoodComponents_d100_v1.txt  

and can be viewed : (this includes viewing bad nodes also)

https://www.fmrib.ox.ac.uk/ukbiobank/group_means/rfMRI_ICA_d25.html
https://www.fmrib.ox.ac.uk/ukbiobank/group_means/rfMRI_ICA_d100.html

For Partial and Full Correlations saved n*(n-1)/2 vectorized elements.  
i)Nodal amplitudes (21 useful/25 and 55 useful/100)  |br|
ii)Partial Correlation Matrix (vectorized and saved upper triangle 210 and 1485)  |br|
iii) Full Correlation Matrix (vectorized and saved upper triangle - 210  elements and 1485) |br|


^^^^^^^^^^^^^^^^^^
Download and Setup
^^^^^^^^^^^^^^^^^^

**UKB_Pipeline**

.. code-block:: shell

   GIT_LFS_SKIP_SMUDGE=1 git clone https://git.upd.unibe.ch/p400pm_191026/istaging_data_consolidation.git IDC_TEMP  
   cd IDC_TEMP/Image_Processing/fMRI
   git lfs pull --include GIGICAR.tar.gz     
   git submodule update --init  UK_biobank_pipeline_v_1

Note : The command `git submodule update --init` will work with `git/2.23.0` & above. Otherwise use `git init`` and then `git submodule add UK_biobank_pipeline_v_1`.  

**GIGICA**  

.. code-block:: shell

   tar xvfz GIGICAR.tar.gz
   rm -rf GIGICAR.tar.gz


**FSLNets**

This is for calculating networks (dependency: MATLAB and L1 precision)  
For more information: https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FSLNets

.. code-block:: shell

   cd IDC_TEMP/Image_Processing/fMRI/UK_biobank_pipeline_v_1
   wget http://www.fmrib.ox.ac.uk/~steve/ftp/fslnets.tar.gz
   tar xvfz fslnets.tar.gz
   rm -rf fslnets.tar.gz

**L1precision**

To estimate L1-norm regularized partial correlation. Here, we are not regularizing/normalizing correlations for now. But its good to get this on path.
.. code-block:: shell

   cd IDC_TEMP/Image_Processing/fMRI/UK_biobank_pipeline_v_1/FSLNets  
   wget http://www.cs.ubc.ca/~schmidtm/Software/L1precision.zip
   unzip L1precision.zip
   rm -rf L1precision.zip


With the setup being complete, now navigate to ~/IDC_TEMP/Image_Processing/fMRI/scripts for running the pipeline.

^^^^^^^^^^
Input Data
^^^^^^^^^^

Step 1 expects data to be in partial BIDS format. And for each subject, folder structure would be for example (runs both structural and functional pipelines and generate T1 brain mask for registration).
The resulting files are `${sub}/fMRI_nosmooth/rfMRI.nii.gz` and `${sub}/T1/T1.nii.gz`.


.. code-block:: shell

   sh convert_to_BIDS.sh -f ${path_to_resting_data} -s ${path_to_t1} -d ${destination} -smooth 0 # or 1
  
This creates the corresponding directory, copies files, and reorients images to LAS.

^^^^^^^^^^^^^^^^^^^^^^
Submitting cluster job
^^^^^^^^^^^^^^^^^^^^^^

This is an example of how to get the pipeline up and running locally. Assuming all wrapper scripts,UKBiobank pipeline and GIGICA are properly cloned:

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Step 1 Filter functional data in MNI152_2mm template space
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Result to look for: `${dest}/${sub}/fMRI_nosmooth/rfMRI.ica/reg_standard/filtered_func_data_clean.nii.gz`

Example command for preprocessing the data:

.. code-block:: shell

    jid=$(qsub \
        -terse \
        -j y \
        -l h_vmem=12G \
        -o ${dest}/${sub}/sge/\$JOB_NAME-\$JOB_ID.log \
        ${path_to_script}/ukbb_fix.sh \
        -s ${sub} \
        -i ${inpath} \
        -tr ${TR} \
        -te ${TE} \
        -fwhm 100 \
        -p ${UKBB_Pipeline_Dir} \
        -smooth 0 );


where sub - subject ID   
      inpath - Path for input directory where subject directory exists(output will be saved in \${inpath}/\${sub})   
      TR - Repetition Time(sec)   
      TE - Echo Time(ms)  
      FWHM - Smoothing parameter - Full Width at Half Max  
      p - location of UKBB pipeline directory   
      -smooth - 0/1 0-no smoothing(uses WHII training data for FIX denoising)  
                    1 - smoothing (uses Standard data for FIX denoising)


^^^^^^
Step 2
^^^^^^

Running GIGICA on filtered functional data separately for 25 and 100 components.

**Result to look for:** \${dest}/\${sub}/\${sub}_gigica.mat which has subject specific time courses and ICs.  
      gigica.mat - ic : nVoxels x nComponents  
                 - tc : nTimecourses x nComponents  

**Other results:** \${sub}_timecourses.nii.gz and \${sub}_componets.nii.gz

Example command for obtaining gigica matrix for an individual:

.. code-block:: shell

    jid=$(qsub \
          -terse \
          -b y \
          -j y \
          -l h_vmem=10G \
          -o ${dest}/${sub}/sge/\$JOB_NAME-\$JOB_ID.log \
          ${path_to_script}/run_GIGICA.sh \
          -in ${filtered_img} \
          -ref ${ref_ics} \
          -mask ${mask_img} \
          -dest ${out_base} \
          -p ${gigica_dir} \
          -a 0.5 );

where in - full path to filtered functional data registered to standard space from previous step (4D file)  
        ref - absolute path to reference group ICs(4D file)  
        mask -  absolute path to MNI152_2mm binarized mask  
        dest - output directory along with  base name
        p - path to GIGICA scripts directory
        a - similarity parameter by default 0.5 (optional) |br|

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Step 3 Extract features from GIGICA matrix
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run separately for 25 and 100 components.

**Result to look for:** Within \${dest}/\${sub}/rfMRI_d100/:

\${sub}_NodeAmplitudes_v1.txt - which has nodal amplitudes of size n=21 or n=55  
\${sub}_partialcorr_v1.txt - partial correlations of size (21x20/2 = 210 elements or 55x54/2 = 1485 elements)  
\${sub}_fullcorr_v1.txt - Full correlations of size (21x20/2 = 210 elements or 55x54/2 = 1485 elements)

Example command for obtaining final features for an individual:

.. code-block:: shell

  jid=$(qsub \
        -terse \
        -b y \
        -j y \
        -l h_vmem=8G \
        -o ${dest}/${sub}/sge/\$JOB_NAME-\$JOB_ID.log \
        ${script}/processing_gigica.sh \
        -s ${sub} \
        -tr ${TR} \
        -iDir ${protoDir}/GIGICA/gigica_d100 \
        -nets ${FSLNets} \
        -p ${ukb} \
        -n  ${nc} \
        -gDir ${ukb}/templates/group/ \
        -tp ${ntp} \
        -o ${dest})


where s - subject ID  
      tr - Repetition Time(sec)  
      iDir - path for GIGICA input result directory  
      nets - path to FSLNets. This must be within UK_biobank_pipeline_v_1 when we clone repository  
      p - path to UKBiobank scripts directory  
      n - number of components(25 or 100)  
      gDir - path to group directory where template for melodic_IC_d25 and melodic_IC_d100 exists.  
      tp - number of timepoints  
      o - destination directory for saving final results.  

### Working Example:

i) Copy data from project:  

.. code-block:: shell

        mkdir \${HOME}/Data/ -pv  
        cp -r /cbica/projects/BLSA/Pipelines/rsfMRI/rsfMRI_2020/Data/Nifti/BLSA_7996_06-0_10/ \${HOME}/Data/

ii) Set all environment variables and paths in settings.sh within scripts directory.


iii) Create destination directory  
.. code-block:: shell

      mkdir \${HOME}/Out/UKB_Pipeline/BLSA_7996_06-0_10/sge -pv


.. code-block:: shell

  sh convert_to_BIDS.sh \
  -f ${HOME}/Data/BLSA_7996_06-0_10/BLSA_7996_06-0_10_REST.nii.gz \
  -s ${HOME}/Data/BLSA_7996_06-0_10/BLSA_7996_06-0_10_T1.nii.gz  \
  -d ${HOME}/Out/UKB_Pipeline/BLSA_7996_06-0_10 \
  -smooth 0


  Expected output is :
      `\${HOME}/Out/UKB_Pipeline/BLSA_7996_06-0_10/fMRI_nosmooth/rfMRI.nii.gz`   
      `\${HOME}/Out/UKB_Pipeline/BLSA_7996_06-0_10/T1/T1.nii.gz`   

For submitting this script to cluster:

.. code-block:: shell

    jid=$(qsub \
          -terse \
          -b y \
          -j y \
          -l short \
          -o ${HOME}/Out/UKB_Pipeline/BLSA_7996_06-0_10/sge/\$JOB_NAME-\$JOB_ID.log \
          $HOME/IDC_TEMP/Image_Processing/fMRI/scripts/convert_to_BIDS.sh \
          -f ${HOME}/Data/BLSA_7996_06-0_10/BLSA_7996_06-0_10_REST.nii.gz \
          -s ${HOME}/Data/BLSA_7996_06-0_10/BLSA_7996_06-0_10_T1.nii.gz  \
          -d ${HOME}/Out/UKB_Pipeline/BLSA_7996_06-0_10 \
          -smooth 0)


  iv) Check Orientation and see if it is LAS:  
   `fslhd \${HOME}/Out/UKB_Pipeline/BLSA_7996_06-0_10/fMRI_nosmooth/rfMRI.nii.gz`   
   `fslhd \${HOME}/Out/UKB_Pipeline/BLSA_7996_06-0_10/T1/T1.nii.gz`

  Expected output:
    `qform_xorient  Right-to-Left`  
    `qform_yorient  Posterior-to-Anterior`  
    `qform_zorient  Inferior-to-Superior`

  v) Next run fmri pipeline by:

.. code-block:: shell

    sh ukbb_fix.sh  \
     -s BLSA_7996_06-0_10 \
     -tr 2 \
     -te 25 \
     -fwhm 100  \
     -p ${HOME}/IDC_TEMP/Image_Processing/fMRI/UK_biobank_pipeline_v_1/  \
     -i ${HOME}/Out/UKB_Pipeline/ \
     -smooth 0

Expected: \${HOME}/Out/UKB_Pipeline/BLSA_7996_06-0_10/fMRI_nosmooth/rfMRI.ica/reg_standard/filtered_func_data_clean.nii.gz (in standard space)

For submitting this script to cluster:

.. code-block:: shell

    jid=$(qsub \
          -terse \
          -b y \
          -j y \
          -l h_vmem=12G \
          -o ${HOME}/Out/UKB_Pipeline/BLSA_7996_06-0_10/sge/\$JOB_NAME-\$JOB_ID.log \
          $HOME/IDC_TEMP/Image_Processing/fMRI/scripts/ukbb_fix.sh \
          -s BLSA_7996_06-0_10 \
          -tr 2 \
          -te 25 \
          -fwhm 100  \
          -p ${HOME}/IDC_TEMP/Image_Processing/fMRI/UK_biobank_pipeline_v_1/  \
          -i ${HOME}/Out/UKB_Pipeline/ \
          -smooth 0)


vi) For GIGICA,

.. code-block:: shell

  mkdir ${HOME}/Out/GIGICA/gigica_d100/BLSA_7996_06-0_10/sge -pv
  sh run_GIGICA.sh \
    -in ${HOME}/Out/UKB_Pipeline/BLSA_7996_06-0_10/fMRI_nosmooth/rfMRI.ica/reg_standard/filtered_func_data_clean.nii.gz \
    -ref ${HOME}/IDC_TEMP/Image_Processing/fMRI/UK_biobank_pipeline_v_1/templates/group/melodic_IC_100.nii.gz  \
    -mask ${HOME}/IDC_TEMP/Image_Processing/fMRI/UK_biobank_pipeline_v_1/templates/MNI152_T1_2mm_brain_mask_bin.nii.gz \
    -dest ${HOME}/Out/GIGICA/gigica_d100/BLSA_7996_06-0_10/BLSA_7996_06-0_10 \
    -p ${HOME}/GIGICAR/ \
    -a 0.5

Pre-requisite: This script takes filtered_func_data_clean in standard space as input which is the output from previous step.  
Expected output:  ``\${HOME}/Out/GIGICA/gigica_d100/BLSA_7996_06-0_10/BLSA_7996_06-0_10_gigica.mat`

The above script runs on MATLAB and exceeds interactive CPU/run limit. It may also use lot of CPUs. To avoid this, it can be submitted as batch job as below .

.. code-block:: shell

    jid=$(qsub \
        -terse \
        -b y \
        -j y \
        -l h_vmem=10G \
        -o ${HOME}/Out/GIGICA/gigica_d100/BLSA_7996_06-0_10/sge/\$JOB_NAME-\$JOB_ID.log \
        $HOME/IDC_TEMP/Image_Processing/fMRI/scripts/run_GIGICA.sh \
        -in ${HOME}/Out/UKB_Pipeline/BLSA_7996_06-0_10/fMRI_nosmooth/rfMRI.ica/reg_standard/filtered_func_data_clean.nii.gz \
        -ref ${HOME}/IDC_TEMP/Image_Processing/fMRI/UK_biobank_pipeline_v_1/templates/group/melodic_IC_100.nii.gz  \
        -mask ${HOME}/IDC_TEMP/Image_Processing/fMRI/UK_biobank_pipeline_v_1/templates/MNI152_T1_2mm_brain_mask_bin.nii.gz \
        -dest ${HOME}/Out/GIGICA/gigica_d100/BLSA_7996_06-0_10/BLSA_7996_06-0_10 \
        -p ${HOME}/IDC_TEMP/Image_Processing/fMRI/GIGICAR/ \
        -a 0.5 )


vii) For Feature Extraction,  


.. code-block:: shell
  mkdir ${HOME}/Out/Features/BLSA_7996_06-0_10/sge -pv
  sh processing_gigica.sh \
    -s BLSA_7996_06-0_10 \
    -tr 2 \
    -iDir ${HOME}/Out/GIGICA/gigica_d100/ \
    -nets ${HOME}/IDC_TEMP/Image_Processing/fMRI/UK_biobank_pipeline_v_1/FSLNets \
    -p ${HOME}/IDC_TEMP/Image_Processing/fMRI/UK_biobank_pipeline_v_1/ \
    -n 100 \
    -gDir ${HOME}/IDC_TEMP/Representation/fMRI/UK_biobank_pipeline_v_1/templates/group/ \
    -tp 180 \
    -o ${HOME}/Out/Features/


Expected output files:|br|
`\${HOME}/Out/Features/BLSA_7996_06-0_10/rfMRI_d100/BLSA_7996_06-0_10_NodeAmplitudes_v1.txt`  |br|
`\${HOME}/Out/Features/BLSA_7996_06-0_10/rfMRI_d100/BLSA_7996_06-0_10_partialcorr_v1.txt`  |br|
`\${HOME}/Out/Features/BLSA_7996_06-0_10/rfMRI_d100/BLSA_7996_06-0_10_fullcorr_v1.txt`

For submitting this script to cluster:

.. code-block:: shell

    jid=$(qsub \
        -terse \
        -b y \
        -j y \
        -l h_vmem=8G \
        -o ${HOME}/Out/Features/BLSA_7996_06-0_10/sge/\$JOB_NAME-\$JOB_ID.log \
        $HOME/IDC_TEMP/Image_Processing/fMRI/scripts/processing_gigica.sh \
        -s BLSA_7996_06-0_10 \
        -tr 2 \
        -iDir ${HOME}/Out/GIGICA/gigica_d100/ \
        -nets ${HOME}/IDC_TEMP/Image_Processing/fMRI/UK_biobank_pipeline_v_1/FSLNets \
        -p ${HOME}/IDC_TEMP/Image_Processing/fMRI/UK_biobank_pipeline_v_1/ \
        -n 100 \
        -gDir ${HOME}/IDC_TEMP/Image_Processing/fMRI/UK_biobank_pipeline_v_1/templates/group/ \
        -tp 180 \
        -o ${HOME}/Out/Features/ )


^^^^^^^^^^
References
^^^^^^^^^^

[1] Miller KL, Alfaro-Almagro F, Bangerter NK, Thomas DL, Yacoub E, Xu J, Bartsch AJ, Jbabdi S, Sotiropoulos SN, Andersson JL, Griffanti L, Douaud G, Okell TW, Weale P, Dragonu I, Garratt S, Hudson S, Collins R, Jenkinson M, Matthews PM, Smith SM. Multimodal population brain imaging in the UK Biobank prospective epidemiological study. Nat Neurosci. 2016 Nov;19(11):1523-1536. doi: 10.1038/nn.4393 . Epub 2016 Sep 19. PMID: 27643430 ; PMCID: PMC5086094. 

[2] L. Griffanti, G. Salimi-Khorshidi, C.F. Beckmann, E.J. Auerbach, G. Douaud, C.E. Sexton, E. Zsoldos, K. Ebmeier, N. Filippini, C.E. Mackay, S. Moeller, J.G. Xu, E. Yacoub, G. Baselli, K. Ugurbil, K.L. Miller, and S.M. Smith. ICA-based artefact removal and accelerated fMRI acquisition for improved resting state network imaging. NeuroImage, 95:232-47, 2014

[3] Du Y, Fan Y. Group information guided ICA for fMRI data analysis. Neuroimage. 2013 Apr 1;69:157-97. doi: 10.1016/j.neuroimage.2012.11.008 . Epub 2012 Nov 27. PMID: 23194820 .  
