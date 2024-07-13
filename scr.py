import subprocess
import json

# Define the range of primary keys you want to dump
start_pk = 1102  # Starting primary key
end_pk = 2000    # Ending primary key

output_file = 'questions_part2.json'  # Output file name

# Open the output file in append mode
with open(output_file, 'a', encoding='utf-8') as f:

    # Loop through the range of primary keys
    for pk in range(start_pk, end_pk + 1):
        # Construct the command
        command = [
            'python', 'manage.py', 'dumpdata',
            'main.question',  # App label and model name
            '--indent', '2',  # Optional: indent for readability
            '--pks', str(pk)  # Specify the primary key
        ]

        try:
            # Execute the command and capture output
            result = subprocess.run(command, capture_output=True, text=True, check=True)

            # Parse JSON output from stdout
            json_data = json.loads(result.stdout)

            # Iterate through each object in the JSON array
            for obj in json_data:
                # Write formatted data to output file
                json.dump(obj, f, indent=2, ensure_ascii=False)
                f.write(',\n')  # Add comma and newline for separation

        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}")

print("Dumpdata process completed.")
