cat ./data/input.csv >> ./data/input_all.csv
python3 ./get_user_info.py
python3 ./submit.py ./data/add.json
