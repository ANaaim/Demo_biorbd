from pathlib import Path
from pyorerun import BiorbdModel,PhaseRerun, PyoMarkers

import numpy as np
import biorbd
from biobuddy import C3dData
import pandas as pd


#
# This examples shows how to
#     1. Load a model
#     2. Generate data (should be acquired via real data)
#     3. Create a Kalman filter
#     4. Apply the Kalman filter (inverse kinematics)
#     5. Plot the kinematics (Q), velocity (Qdot) and acceleration (Qddot)
#
# Please note that this example will work only with the Eigen backend.
# Please also note that kalman will be VERY slow if compiled in debug
#


def main(filename, model_name, show: bool = True):
    # Load a predefined model
    model = biorbd.Model(model_name)
    trial = C3dData(filename)
    nb_frames = trial.nb_frames
    name_dofs = [model.nameDof()[i].to_string() for i in range(model.nbQ())]
    dict_dof = {}
    for ind,name in enumerate(name_dofs):
        dict_dof[name] = ind

    first_frame = trial.ezc3d_data.parameters["PROCESSING"]["Cropped Measurement Start Frame"]["value"][0]
    last_frame = trial.ezc3d_data.parameters["PROCESSING"]["Cropped Measurement End Frame"]["value"][0]
    print(f"First frame: {first_frame}, last frame: {last_frame}")
    
    markerNames = [model.markerNames()[i].to_string() for i in range(len(model.markerNames()))]
    markers = trial.get_position(markerNames)[:3,:,:]
    IK = biorbd.InverseKinematics(model, markers)
    q_recons = IK.solve()
    #q_2_export = q_recons[[dict_dof["Head_RotZ"]]]
    

    # export a csv of the kinematics containing the head rotation and the first frame time 
    
    # # Compute time vector based on frame count and sampling frequency
    # frame = np.arange(first_frame, last_frame, dtype=int)
    # # Extract Head_RotZ values
    # head_rot_z = q_recons[dict_dof["Head_RotZ"], :]

    # # Create DataFrame
    # df = pd.DataFrame({
    #     "TimFramee (s)": frame,
    #     "Head_RotZ": head_rot_z
    # })

    # # Export to CSV in the same directory as the input file
    # name_csv = Path(filename).with_suffix(".csv")
    # df.to_csv(name_csv, index=False)
    # print(f"Exported kinematics to {name_csv}")
    
    if show:
        nb_seconds = 3
        t_span = np.linspace(0, nb_seconds, nb_frames)
        model.name = "toto"
        model.markerNames
        model.nb_markers = len(model.markerNames())
        model.marker_names = model.markerNames()
        #model.options.show_gravity = False
        model_rerun = BiorbdModel(model_name)
        viz = PhaseRerun(t_span)
        viz.add_animated_model(model_rerun, q_recons,tracked_markers=PyoMarkers(data=markers, channels=markerNames,show_labels=False))
        viz.rerun("msk_model")
        # pause to see the model
        input("Press Enter to continue...")

    return q_recons,dict_dof

if __name__ == "__main__":
    q_recons,dict_dof = main("20250807_LR_H90G90_final.c3d", "lower_body.bioMod", show=True)
    print(np.mean(q_recons[[dict_dof["LTibia_RotX"]], :])*180/np.pi)  # in degrees