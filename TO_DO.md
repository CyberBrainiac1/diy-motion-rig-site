# TO DO

## Safety audit for the 20 scenario slide

The current design already has some real protection:

- `60A` main ANL fuse
- `30A` branch fuse on each motor side
- `E-stop -> contactor coil -> power removed`
- PSU overload protection
- PSU thermal protection
- regen-capable motor driver
- fixed base with limited motion range

That means the rig is **not unprotected**. But some scenarios are only **partly covered** right now, and a few still depend too much on procedure or fast human reaction.

## Already covered reasonably well

- `Main power wire shorts`
  Current protection: `60A` main fuse near the PSU
- `One motor branch shorts`
  Current protection: `30A` branch fuse on that side
- `PSU overloads`
  Current protection: Mean Well overload protection
- `PSU overheats`
  Current protection: PSU thermal shutdown
- `House power cuts out`
  Current protection: motors de-energize when supply disappears

## Partly covered, but should be improved

- `Water falls on wires`
  Current protection: fuses if it becomes a hard short
  Gap: no liquid detection, and water may still damage wiring before a full short happens
  To do:
  - raise wiring off the floor
  - add split loom or sleeving on exposed runs
  - add cable clips / strain relief so wires cannot sag into bad locations
  - make a strict no-drinks-near-rig rule

- `Metal tool falls across terminals`
  Current protection: fuse path if it creates a direct short
  Gap: the short can still be violent before the fuse opens
  To do:
  - add terminal covers / insulated boots
  - cover exposed high-current studs
  - keep an insulated tool rule near the electrical area

- `Loose wire touches frame`
  Current protection: fuse if it becomes a true short
  Gap: rubbing damage can exist before a fuse ever blows
  To do:
  - add grommets where wires pass edges
  - add P-clamps or zip-tie anchors for routing
  - inspect wire rub points during every test session

- `Motor jams hard`
  Current protection: driver + fuse path reduce electrical escalation
  Gap: there is no explicit stall-detection layer in the plan yet
  To do:
  - keep startup on a low-force profile
  - add software current / output limits if available
  - add a rule to stop immediately if one side sounds loaded or stalled

- `Rig suddenly moves wrong`
  Current protection: E-stop
  Gap: this still depends on operator reaction
  To do:
  - make the first test profile very weak by default
  - add a startup rule: motion stays disabled until the operator is seated and ready
  - keep the E-stop in the natural hand path

- `Motion feels dangerous`
  Current protection: E-stop + retuning
  Gap: still mostly reaction-based
  To do:
  - start with lower output percentages
  - add software ramp limits / smoothing
  - keep a separate low-power tuning profile

- `Hand or tool is inside`
  Current protection: unplug-before-service procedure
  Gap: procedure only
  To do:
  - make a hard rule: unplug before touching linkage
  - put a visible service tag on the rig during work
  - never tune with hands near moving parts

- `Child or pet gets close`
  Current protection: E-stop / power-down
  Gap: no automatic detection
  To do:
  - define a clear operating zone around the rig
  - do not run the rig unless the area is clear
  - add a master power switch or unplug rule when the rig is not in use

## Not fully protected yet and should be fixed before real use

- `Water splashes on PSU`
  Current protection: manual shutdown only
  Gap: water on mains-powered hardware is not automatically managed
  To do:
  - mount the PSU higher and away from likely spill zones
  - add a simple splash guard / cover with airflow
  - use a GFCI-protected outlet or power strip
  - keep a strict no-drinks rule near the rig

- `Smoke appears`
  Current protection: cut power immediately
  Gap: this is an emergency response, not a true automatic protection
  To do:
  - keep an extinguisher nearby
  - make sure the wall plug or power strip is easy to reach
  - never leave the rig powered unattended
  - do short first-power tests instead of long sessions

- `Something catches fire`
  Current protection: cut wall power + extinguisher
  Gap: again, this is emergency response rather than built-in prevention
  To do:
  - keep an extinguisher in the room
  - keep a clear exit path
  - avoid clutter near the PSU and wiring
  - do not operate near flammable materials

- `Linkage bolt loosens`
  Current protection: careful assembly / inspection
  Gap: no secondary retention shown yet
  To do:
  - use nyloc nuts or threadlocker where appropriate
  - add witness marks on critical fasteners
  - make a quick pre-run bolt check list

- `Rod-end joint pops off`
  Current protection: correct assembly only
  Gap: no visible secondary retention plan yet
  To do:
  - use proper rod-end hardware and spacers
  - add safety washers / retention where possible
  - inspect rod ends for play before use

- `Crank bolt loosens`
  Current protection: careful fastening only
  Gap: no extra anti-loosening measure described yet
  To do:
  - use a locking method appropriate for the crank joint
  - add witness marks
  - re-check after first few motion tests

- `Frame wood starts cracking`
  Current protection: stop using it
  Gap: no crack detection or reinforcement plan yet
  To do:
  - inspect all high-load joints often
  - add gussets or reinforcement plates if any area looks stressed
  - spread bolt loads with washers / plates where needed

## Best next upgrades before first powered motion

If only a few upgrades happen before first motion testing, these are the highest-value ones:

1. terminal covers / insulated boots on exposed high-current connections
2. splash protection + raised mounting for the PSU
3. GFCI-protected outlet or power strip
4. nyloc / threadlocker + witness marks on critical linkage bolts
5. extinguisher nearby and short supervised first-power tests
6. low-power startup profile with the E-stop always within reach

## Honest summary

The current design already has **real electrical protection**, but it does **not yet have a complete protection layer for liquids, fire response, loose hardware detection, or people entering the motion area**.

Those items should stay on the build checklist instead of being claimed as already solved.
