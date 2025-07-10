# COMP_PROMPT = """In the future, if I provide the drawings before and after the change( the first one is befor and the second one is after), you are the world's best geotechnical and 
# earthwork experts, and by analyzing the differences between the two drawings based on the following matters. (Example: cip → slope)  
#  -Changes: Location (spaces, distance from borderline, etc.), shape (curve → straight line, change of wall connections, etc.) -Dosing
#    method: CIP, earth plate, SCW, diaphragm wall, etc.     2. Check the changes in the climax method. (Example: RAKER → Anchor, etc.) 
#        -Dosing method of earthenware: RAKER, Anchor, Strut, etc.     3. Compare the excavation level (EL) change (notation position and
#          additional, level value, etc.).   -Changes: Excavation level value change (e.g. el (-) 12.0 → EL (-) 13.0)     4. Check the 
#          changes in the soil component elements (for example, H-PILE, WALE, ANCHOR, RAKER, etc.).   -Changes: H-PILE 
#          specifications (for example, H-300x300x10x15 (C.T.C1800) → H-300x200x9x14 (C.T.C900)), WALE specifications 
#          (e.g. H-300x300x10x15/H-300x305x15x15 → 2H-300x9x914), Anchor standards and spacing, raker spacing, etc.    
#            5. Check the order plan change.   -Changes: In addition to changing the order method (e.g. SGR → ESG, Silica series, etc.) 
#            -Type of ordering method: SGR, ESG, ASG, Silica -based ordering method, etc.     6. Check the changes in other drawings.
#              (Example: Motor Position Change, Legends and Note Additional Materials, etc.)  
#             -Changes: Moving or adding new positions, fertilization or omission of legend symbols, additional or deletion, cross -sectional or section change"""


COMP_PROMPT = """I provided the drawings before and after the change( the first one is befor and the second one is after), you are the world's best geotechnical and 
earthwork experts, and by analyzing the differences between the two drawings based on the following matters. (Example: cip → slope)  
 -Changes: Location (spaces, distance from borderline, etc.), shape (curve → straight line, change of wall connections, etc.) -Dosing
   method: CIP, earth plate, SCW, diaphragm wall, etc.     2. Check the changes in the climax method. (Example: RAKER → Anchor, etc.) 
       -Dosing method of earthenware: RAKER, Anchor, Strut, etc.     3. Compare the excavation level (EL) change (notation position and
         additional, level value, etc.).   -Changes: Excavation level value change (e.g. el (-) 12.0 → EL (-) 13.0)     4. Check the 
         changes in the soil component elements (for example, H-PILE, WALE, ANCHOR, RAKER, etc.).   -Changes: H-PILE 
         specifications (for example, H-300x300x10x15 (C.T.C1800) → H-300x200x9x14 (C.T.C900)), WALE specifications 
         (e.g. H-300x300x10x15/H-300x305x15x15 → 2H-300x9x914), Anchor standards and spacing, raker spacing, etc.    
           5. Check the order plan change.   -Changes: In addition to changing the order method (e.g. SGR → ESG, Silica series, etc.) 
           -Type of ordering method: SGR, ESG, ASG, Silica -based ordering method, etc.     6. Check the changes in other drawings.
             (Example: Motor Position Change, Legends and Note Additional Materials, etc.)  
            -Changes: Moving or adding new positions, fertilization or omission of legend symbols, additional or deletion, cross -sectional or section change"""