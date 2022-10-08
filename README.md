# Team WWU_Muenster 2022 Software Tool

## Description

### Introduction:
The goal of metabolic engineering for industrial applications is the overproduction of metabolites with the help of organisms. While the field originated from single modifications in metabolic pathways, today’s approaches for metabolic engineering include a much more systematic view on biological systems. This is largely fueled by advances in computational methods ([Woolston, Edgar and Stephanopoulos, 2013](https://www.annualreviews.org/doi/10.1146/annurev-chembioeng-061312-103312)). One of most prominent computational methods in metabolic engineering is flux balance analysis (FBA) of genome-scale metabolic models (GSMMs). In brief, GSMMs are mathematical representations of all known chemical reactions within an organism. FBA calculates the respective fluxes through all the reactions of a GSMM, based on certain mathematical constraints ([Orth, Thiele and Palsson, 2010](https://www.nature.com/articles/nbt.1614#MOESM178)). To learn more about the general background of FBA and GSMMs, take a look at our [modeling page](https://2022.igem.wiki/wwu-muenster/model). 
Many FBA- and GSMM-based tools are available to find genetic targets for metabolic engineering. Most available software tools, however, focus on predicting gene knockout effects and do not include the identification of putative gene amplification targets. Flux scanning based on enforced objective flux (FSEOF) is a prominent algorithm for identifying gene amplification targets and has been successfully used to optimize cell factories ([Choi et al., 2010](https://journals.asm.org/doi/10.1128/AEM.00115-10); [Park et al., 2012](https://journals.asm.org/doi/10.1128/AEM.00115-10)). As no stand-alone FSEOF software tool is currently available and, to the best of our knowledge, no public code repositories can be found online, we decided to develop a user-friendly command line tool that utilizes the FSEOF algorithm for the identification of genetic overexpression and downregulation targets. 

### Considerations:
When we started to apply FBA- and GSMMs-based tools for the modeling of our MonChassis yeast strains, we quickly experienced that the available tools and methods can be difficult to use if you do not have any experience with FBA and GSMMs. Many tools are available in the COBRA toolbox for MATLAB. However, the usage of the COBRA toolbox requires a MATLAB license and knowledge in the MATLAB programming language. Even though iGEM teams had free access to MATLAB for the period of their project in the recent years, many members of the iGEM community could benefit from free access to software tools for metabolic engineering after their iGEM project ends. Hence, we wanted our software to be as accessible as possible and easy to use, especially for users with only little experience with FBA and GSMMs. We aimed that our software can be used without knowledge in programming and only to be fully build on the foundation of open-source libraries.


### Installation & Usage

1. Make sure you have python installed on your computer
2. Download the FSEOF GitLab repository as a zip file
3. Unzip the downloaded zip file
4. Move the "wwu-muenster-main" folder to the desired destination on your computer
 > Note: You can rename the folder if you like
5. Paste the .xml file of your SBML model into the folder "wwu-muenster-main"
 6. Navigate to the folder in the terminal of your computer. Users without knowledge of navigation in the terminal have the following options:
 > - **Windows:** Open the parent folder in the file explorer - Hold "Shift" and right-click on the "wwu-muenster-main" folder – select "Open PowerShell here"
> - **MacOS:** Open the parent folder in the finder – right-click on the "wwu-muenster-main" folder – select "New terminal at Folder"
 7. In the now opened terminal window type in the following line and press enter. **This is only necessary for the first time you use the tool!**
    
    ´pip install -r requirements.txt´
  
8. Type in ´python run_FSEOF.py NameOfYourSBMLFile BiomassID reactionID´ and press enter. The results are stored in an excel file
> **Example:** ´python run_FSEOF.py yeast_gem.xml r_4041 r_4269


## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started.
Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps
explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce
the likelihood that the changes inadvertently break something. Having instructions for running tests is especially
helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.
