"""
This example shows how to create a personalized kinematic model from a C3D file containing a static trial.
Here, we generate a simple lower-body model with only a trunk segment.
The marker position and names are taken from Maldonado & al., 2018 (https://hal.science/hal-01841355/)
"""

import os

import numpy as np
from biobuddy import (
    Axis,
    BiomechanicalModel,
    C3dData,
    Marker,
    Mesh,
    Segment,
    SegmentCoordinateSystem,
    Translations,
    Rotations,
    DeLevaTable,
    Sex,
    SegmentName,
    ViewAs,
    SegmentCoordinateSystemUtils,
    RotoTransMatrix,
)


def model_creation_from_measured_data(static_trial: C3dData, remove_temporary: bool = True, animate_model: bool = True):

    total_mass = 66
    total_height = 1.70

    output_model_filepath = f"lower_body.bioMod"


    # Generate the personalized kinematic model
    reduced_model = BiomechanicalModel()

    reduced_model.add_segment(Segment(name="Ground"))

    reduced_model.add_segment(
        Segment(
            name="Pelvis",
            parent_name="Ground",
            translations=Translations.XYZ,
            rotations=Rotations.XYZ,
            segment_coordinate_system=SegmentCoordinateSystem(
                origin=SegmentCoordinateSystemUtils.mean_markers(["LPSIS", "RPSIS", "LASIS", "RASIS"]),
                first_axis=Axis(
                    name=Axis.Name.X,
                    start=SegmentCoordinateSystemUtils.mean_markers(["LPSIS", "LASIS"]),
                    end=SegmentCoordinateSystemUtils.mean_markers(["RPSIS", "RASIS"]),
                ),
                second_axis=Axis(name=Axis.Name.Z),
                axis_to_keep=Axis.Name.Z,
            ),
            mesh=Mesh(("LMSIS", "RASIS", "LASIS", "LMSIS"), is_local=False),
        )
    )

    reduced_model.segments["Pelvis"].add_marker(Marker("LASIS", is_technical=True, is_anatomical=True))
    reduced_model.segments["Pelvis"].add_marker(Marker("RASIS", is_technical=True, is_anatomical=True))
    reduced_model.segments["Pelvis"].add_marker(Marker("RMSIS", is_technical=True, is_anatomical=True))
    reduced_model.segments["Pelvis"].add_marker(Marker("LMSIS", is_technical=True, is_anatomical=True))

    reduced_model.add_segment(
        Segment(
            name="RFemur",
            parent_name="Pelvis",
            rotations=Rotations.XYZ,
            segment_coordinate_system=SegmentCoordinateSystem(
                origin=lambda m, bio: SegmentCoordinateSystemUtils.mean_markers(["RPSIS", "RASIS"])(
                    static_trial.values, None
                )
                - np.array([0.0, 0.0, 0.05 * total_height, 0.0]),
                first_axis=Axis(name=Axis.Name.X, start="RME", end="RLE"),
                second_axis=Axis(
                    name=Axis.Name.Z,
                    start=SegmentCoordinateSystemUtils.mean_markers(["RME", "RLE"]),
                    end=SegmentCoordinateSystemUtils.mean_markers(["RPSIS", "RASIS"]),
                ),
                axis_to_keep=Axis.Name.Z,
            ),
            mesh=Mesh(
                (
                    lambda m, bio: SegmentCoordinateSystemUtils.mean_markers(["RPSIS", "RASIS"])(
                        static_trial.values, None
                    )
                    - np.array([0.0, 0.0, 0.05 * total_height, 0.0]),
                    "RME",
                    "RLE",
                    lambda m, bio: SegmentCoordinateSystemUtils.mean_markers(["RPSIS", "RASIS"])(
                        static_trial.values, None
                    )
                    - np.array([0.0, 0.0, 0.05 * total_height, 0.0]),
                ),
                is_local=False,
            ),
        )
    )
    reduced_model.segments["RFemur"].add_marker(Marker("RGT", is_technical=True, is_anatomical=True))
    reduced_model.segments["RFemur"].add_marker(Marker("RLE", is_technical=True, is_anatomical=True))
    reduced_model.segments["RFemur"].add_marker(Marker("RME", is_technical=True, is_anatomical=True))

    # reduced_model.add_segment(
    #     Segment(
    #         name="RTibia",
    #         parent_name="RFemur",
    #         rotations=Rotations.X,
    #         inertia_parameters=de_leva[SegmentName.SHANK],
    #         segment_coordinate_system=SegmentCoordinateSystem(
    #             origin=SegmentCoordinateSystemUtils.mean_markers(["RMFE", "RLFE"]),
    #             first_axis=Axis(name=Axis.Name.X, start="RSPH", end="RLM"),
    #             second_axis=Axis(
    #                 name=Axis.Name.Z,
    #                 start=SegmentCoordinateSystemUtils.mean_markers(["RSPH", "RLM"]),
    #                 end=SegmentCoordinateSystemUtils.mean_markers(["RMFE", "RLFE"]),
    #             ),
    #             axis_to_keep=Axis.Name.Z,
    #         ),
    #         mesh=Mesh(("RMFE", "RSPH", "RLM", "RLFE"), is_local=False),
    #     )
    # )
    # reduced_model.segments["RTibia"].add_marker(Marker("RHF", is_technical=True, is_anatomical=True))
    # reduced_model.segments["RTibia"].add_marker(Marker("RTT", is_technical=True, is_anatomical=True))

    # The foot is a special case since the position of the ankle relatively to the foot length is not given in De Leva
    # So here we assume that the foot com is in the middle of the three foot markers

    # reduced_model.add_segment(
    #     Segment(
    #         name="RFoot",
    #         parent_name="RTibia",
    #         rotations=Rotations.X,
    #         segment_coordinate_system=SegmentCoordinateSystem(
    #             origin=SegmentCoordinateSystemUtils.mean_markers(["RSPH", "RLM"]),
    #             first_axis=Axis(
    #                 Axis.Name.Z, start=SegmentCoordinateSystemUtils.mean_markers(["RSPH", "RLM"]), end="RTT2"
    #             ),
    #             second_axis=Axis(Axis.Name.X, start="RSPH", end="RLM"),
    #             axis_to_keep=Axis.Name.Z,
    #         ),
    #         inertia_parameters=foot_inertia_parameters,
    #         mesh=Mesh(("RLM", "RTT2", "RSPH", "RLM"), is_local=False),
    #     )
    # )
    # reduced_model.segments["RFoot"].add_marker(Marker("RTT2", is_technical=True, is_anatomical=True))

    reduced_model.add_segment(
        Segment(
            name="LFemur",
            parent_name="Pelvis",
            rotations=Rotations.XYZ,
            segment_coordinate_system=SegmentCoordinateSystem(
                origin=lambda m, bio: SegmentCoordinateSystemUtils.mean_markers(["LPSIS", "LASIS"])(
                    static_trial.values, None
                )
                - np.array([0.0, 0.0, 0.05 * total_height, 0.0]),
                first_axis=Axis(name=Axis.Name.X, start="LLE", end="LME"),
                second_axis=Axis(
                    name=Axis.Name.Z,
                    start=SegmentCoordinateSystemUtils.mean_markers(["LME", "LLE"]),
                    end=SegmentCoordinateSystemUtils.mean_markers(["LPSIS", "LASIS"]),
                ),
                axis_to_keep=Axis.Name.Z,
            ),
            mesh=Mesh(
                (
                    lambda m, bio: SegmentCoordinateSystemUtils.mean_markers(["LPSIS", "LASIS"])(
                        static_trial.values, None
                    )
                    - np.array([0.0, 0.0, 0.05 * total_height, 0.0]),
                    "LME",
                    "LLE",
                    lambda m, bio: SegmentCoordinateSystemUtils.mean_markers(["LPSIS", "LASIS"])(
                        static_trial.values, None
                    )
                    - np.array([0.0, 0.0, 0.05 * total_height, 0.0]),
                ),
                is_local=False,
            ),
        )
    )
    reduced_model.segments["LFemur"].add_marker(Marker("LGT", is_technical=True, is_anatomical=True))
    reduced_model.segments["LFemur"].add_marker(Marker("LLE", is_technical=True, is_anatomical=True))
    reduced_model.segments["LFemur"].add_marker(Marker("LME", is_technical=True, is_anatomical=True))

    reduced_model.add_segment(
        Segment(
            name="LTibia",
            parent_name="LFemur",
            rotations=Rotations.XYZ,
            segment_coordinate_system=SegmentCoordinateSystem(
                origin=SegmentCoordinateSystemUtils.mean_markers(["LME", "LLE"]),
                first_axis=Axis(name=Axis.Name.X, start="LLM", end="LMM"),
                second_axis=Axis(
                    name=Axis.Name.Z,
                    start=SegmentCoordinateSystemUtils.mean_markers(["LMM", "LLM"]),
                    end=SegmentCoordinateSystemUtils.mean_markers(["LME", "LLE"]),
                ),
                axis_to_keep=Axis.Name.Z,
            ),
            mesh=Mesh(("LME", "LMM", "LLM", "LLE"), is_local=False),
        )
    )

    reduced_model.segments["LTibia"].add_marker(Marker("LHF", is_technical=True, is_anatomical=True))
    reduced_model.segments["LTibia"].add_marker(Marker("LTT", is_technical=True, is_anatomical=True))
    reduced_model.segments["LTibia"].add_marker(Marker("LLM", is_technical=True, is_anatomical=True))
    reduced_model.segments["LTibia"].add_marker(Marker("LMM", is_technical=True, is_anatomical=True))



    # Put the model together, print it and print it to a bioMod file
    model_real = reduced_model.to_real(static_trial)
    model_real.to_biomod(output_model_filepath)

    if animate_model:
        model_real.animate(view_as=ViewAs.BIORBD, model_path=output_model_filepath)

    if remove_temporary:
        os.remove(output_model_filepath)

    return model_real


def main():

    # Load the static trial
    static_trial = C3dData(f"20250807_LR_debout.c3d")

    model_creation_from_measured_data(static_trial, remove_temporary=False, animate_model=True)


if __name__ == "__main__":
    main()
