#! /usr/bin/env python
#=========================================================================
# construct.py
#=========================================================================

import os
import sys

from mflowgen.components import Graph, Step

def construct():

  g = Graph()
  g.sys_path.append( '/farmshare/home/classes/ee/272' )

  #-----------------------------------------------------------------------
  # Parameters
  #-----------------------------------------------------------------------
  
  adk_name = 'skywater-130nm-adk.v2021'
  adk_view = 'view-standard'

  parameters = {
    'construct_path' : __file__,
    'design_name'    : 'Conv',
    'adk'            : adk_name,
    'adk_view'       : adk_view,
    'topographical'  : True,
    'strip_path'     : 'scverify/Conv',
    'saif_instance'  : 'scverify/Conv'
  }

  #-----------------------------------------------------------------------
  # Create nodes
  #-----------------------------------------------------------------------

  this_dir = os.path.dirname( os.path.abspath( __file__ ) )

  # ADK step

  g.set_adk( adk_name )
  adk = g.get_adk_step()

  # Custom steps

  sram          = Step( this_dir + '/sram'          )
  rtl           = Step( this_dir + '/rtl'           )
  constraints   = Step( this_dir + '/constraints'   )

  # Default steps

  info         = Step( 'info',                          default=True )
  dc           = Step( 'synopsys-dc-synthesis',         default=True )
  #rtl_sim      = Step( 'synopsys-vcs-sim',              default=True )
  gen_saif     = Step( 'synopsys-vcd2saif-convert',     default=True )
  #gen_saif_rtl = gen_saif.clone()
  #gen_saif_rtl.set_name( 'gen-saif-rtl' )

  #-----------------------------------------------------------------------
  # Graph -- Add nodes
  #-----------------------------------------------------------------------

  g.add_step( info         )
  g.add_step( sram         )
  g.add_step( rtl          )
  g.add_step( constraints  )
  g.add_step( dc           )
  #g.add_step( rtl_sim     )
  g.add_step( gen_saif     )

  #-----------------------------------------------------------------------
  # Graph -- Add edges
  #-----------------------------------------------------------------------
  
  # Dynamically add edges

  dc.extend_inputs(['sky130_sram_1kbyte_1rw1r_32x256_8_tt_1p8V_25C.db', 'sky130_sram_2kbyte_1rw1r_32x512_8_tt_1p8V_25C.db'])
  #rtl_sim.extend_inputs(['sky130_sram_1kbyte_1rw1r_32x256_8.v', 'sky130_sram_2kbyte_1rw1r_32x512_8.v'])

  # Connect by name

  g.connect_by_name( adk,          dc           )
  g.connect_by_name( sram,         dc           )
  g.connect_by_name( rtl,          dc           )
  g.connect_by_name( constraints,  dc           )
  #g.connect_by_name( rtl,          rtl_sim      ) 
  #g.connect_by_name( sram,         rtl_sim      ) 
  g.connect( rtl.o( 'run.vcd' ), gen_saif.i( 'run.vcd' ) )
  g.connect_by_name( gen_saif, dc           ) # run.saif

  g.param_space(dc, "clock_period", [2.0, 4.0, 5.0, 10.0, 20.0, 100.0, 500.0])

  #-----------------------------------------------------------------------
  # Parameterize
  #-----------------------------------------------------------------------

  g.update_params( parameters )

  return g

if __name__ == '__main__':
  g = construct()
  g.plot()
