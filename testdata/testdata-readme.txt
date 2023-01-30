All the test data are derived directly from free-access data.
The test data provided only for the purpose of demonstration of ProHiC fuctionality.
Detailed list of files and their origins below.



Caulobacter/

Caulobacter.mcool - Hi-C map of C. crescentus, converted from matrix file deposited in GEO (GSE45966, GSM1120448) as a material for the paper:
Le TB, Imakaev MV, Mirny LA, Laub MT. High-resolution mapping of the spatial organization of a bacterial chromosome. Science. 2013;342(6159):731-734. doi:10.1126/science.1242059.

Caulobacter_GC-skew.bedgraph - GC-skew, calculated by us on the base of the genome CP001340.1.

Caulobacter_ori-ter.bed - replication origin and terminator, taken from the paper above and another one:
Jensen RB. Analysis of the terminus region of the Caulobacter crescentus chromosome and identification of the dif site. J Bacteriol. 2006;188(16):6016-6019. doi:10.1128/JB.00330-06.

Caulobacter_*.gff3 - selected genes from genome annotation, available at CP001340.1.



Sulfolobus/

Sulfolobus.mcool - Hi-C map of S. acidocaldarius, converted from matrix file deposited in GEO (GSE128063, GSM4832101) as a material for the paper:
Takemata N, Samson RY, Bell SD. Physical and Functional Compartmentalization of Archaeal Chromosomes. Cell. 2019;179(1):165-179.e18. doi:10.1016/j.cell.2019.08.036.

Sulfolobus_RNA-seq.bedgraph - RNA-seq graph of S. acidocaldarius, converted from file deposited in GEO (GSE128063, GSM3662081) as a material for the paper above.

Sulfolobus_*.gff3 - selected genes from genome annotation, available at NZ_CP020364.1. Annotation date 12/30/2022 04:02:39.

Sulfolobus_GC-skew.bedgraph - GC-skew, calculated by us on the base of the genome NZ_CP020364.1.

Sulfolobus_ori.bed - Replication origins, taken from the paper:
Duggin IG, McCallum SA, Bell SD. Chromosome replication dynamics in the archaeon Sulfolobus acidocaldarius. Proc Natl Acad Sci U S A. 2008;105(43):16737-16742. doi:10.1073/pnas.0806414105.



Haloferax/

Haloferax.mcool - Hi-C map of H. volcanii, computed by us on the base of:
1) H26 genome, derived in accordance with the paper below from DS2 genome (GCF_000025685.1), which is the subject of the paper:
Hartman AL, Norais C, Badger JH, et al. The complete genome sequence of Haloferax volcanii DS2, a model archaeon. PLoS One. 2010;5(3):e9605. Published 2010 Mar 19. doi:10.1371/journal.pone.0009605.
2) Raw reads deposited in PRJNA587586 (SRR11747717) as a material for the paper:
Cockram C, Thierry A, Gorlas A, Lestini R, Koszul R. Euryarchaeal genomes are folded into SMC-dependent loops and domains, but lack transcription-mediated compartmentalization. Mol Cell. 2021;81(3):459-472.e10. doi:10.1016/j.molcel.2020.12.013.

Haloferax_RNA-seq.bedgraph - RNA-seq of H. volcanii, computed by us on the base of raw reads deposited in SRR11747728, as a material for the paper above.

Haloferax_*.gff3 - selected genes from genome annotation, available at NC_013967.1. Coordinates updated to match genome manipulations above. Annotation date 01/08/2023 09:53:24