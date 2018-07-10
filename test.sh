#!/bin/bash
source ../p2dn/bin/activate
# for file in ./models/*.npy
# do
#     filename=$(basename "$file")
#     filename="${filename%.*}"
#     python main.py --phase=test --model_file="${file}" --beam_size=3"
# done
# exit 0

file=289999.npy
python main.py --phase=test --model_file="./models/${file}" --beam_size=3
