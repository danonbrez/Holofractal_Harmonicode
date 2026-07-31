#include "hhs_p183.h"
#include <stdio.h>
#include <string.h>
int main(int argc,char**argv){hhs_p183_context*ctx;char identity[65];if(argc!=2){fprintf(stderr,"usage: hhs-probability-native <exact-equation>\n");return 2;}ctx=hhs_p183_context_create();if(ctx==NULL)return 2;if(hhs_p183_parse_equation(ctx,argv[1],strlen(argv[1]))!=P183_OK||hhs_p183_build_membrane_tree(ctx)!=P183_OK||hhs_p183_validate_membrane_boundaries(ctx)!=P183_OK||hhs_p183_snapshot_lexical_identity(ctx,identity)!=P183_OK){fprintf(stderr,"Status: P183_REJECT_PARSE_OR_MEMBRANE\n");hhs_p183_context_destroy(ctx);return 1;}printf("Status: P183_OK\nEquation identity: %s\nMembranes: %zu\n",identity,hhs_p183_membrane_count(ctx));hhs_p183_context_destroy(ctx);return 0;}
