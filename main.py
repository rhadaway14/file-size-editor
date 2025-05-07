import os
import json
import argparse


def split_json_array(input_file, output_dir, prefix, max_size_bytes=40):
    # open file and get result values
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f).get("results")
    if not isinstance(data, list):
        raise ValueError("Input JSON must contain a top-level 'results' array.")

    # confirm output dir
    os.makedirs(output_dir, exist_ok=True)

    chunk_index = 1
    out_path = os.path.join(output_dir, f"{prefix}_{chunk_index:03d}.json")
    f_out = open(out_path, 'w', encoding='utf-8')
    f_out.write('[')
    current_size = len('['.encode('utf-8'))
    first = True

    for item in data:
        item_str = json.dumps(item, ensure_ascii=False, separators=(',', ':'))

        sep = '' if first else ','
        projected_size = current_size \
                         + len(sep.encode('utf-8')) \
                         + len(item_str.encode('utf-8')) \
                         + len(']'.encode('utf-8'))

        if not first and projected_size > max_size_bytes*1024*1024:
            f_out.write(']')
            f_out.close()
            print(f"Wrote {out_path} ({os.path.getsize(out_path)} bytes)")

            chunk_index += 1
            out_path = os.path.join(output_dir, f"{prefix}_{chunk_index:03d}.json")
            f_out = open(out_path, 'w', encoding='utf-8')
            f_out.write('[')
            current_size = len('['.encode('utf-8'))
            first = True

        f_out.write(sep + item_str)
        current_size += len(sep.encode('utf-8')) + len(item_str.encode('utf-8'))
        first = False

    f_out.write(']')
    f_out.close()
    print(f"Wrote {out_path} ({os.path.getsize(out_path)} bytes)")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Stream-split a JSON array under "results" into chunks ≤ max size.')
    parser.add_argument('input', help='Input JSON file with top-level "results" array')
    parser.add_argument('output_dir', help='Directory to write chunk files into')
    parser.add_argument('--prefix', default='chunk', help='Filename prefix (default "chunk")')
    parser.add_argument('--max-size', type=int, default=40, help='Max bytes per chunk (default 40MB)')
    args = parser.parse_args()
    split_json_array(args.input, args.output_dir, args.prefix, args.max_size)
