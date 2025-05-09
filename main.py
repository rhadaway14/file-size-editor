import os
import json
import argparse


def split_json_array(input_file, output_dir, prefix, max_size_bytes=40 * 1024 * 1024):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f).get("results")
    if not isinstance(data, list):
        raise ValueError('Input JSON must contain a top-level "results" array.')

    os.makedirs(output_dir, exist_ok=True)

    chunk_index = 1
    f_out = None
    current_size = 0
    first = True

    def open_new_chunk():
        nonlocal f_out, current_size, first, chunk_index
        # Close previous chunk (if any)
        if f_out:
            f_out.write(']')
            f_out.close()
            print(f"Wrote {out_path} ({os.path.getsize(out_path)} bytes)")
            chunk_index += 1

        out_path_local = os.path.join(output_dir, f"{prefix}_{chunk_index:03d}.json")
        f = open(out_path_local, 'w', encoding='utf-8')
        f.write('[')
        # reset counters for the new file
        current_size = len('['.encode('utf-8'))
        first = True
        f_out = f
        return out_path_local

    out_path = open_new_chunk()

    for item in data:
        item_str = json.dumps(item, ensure_ascii=False, separators=(',', ':'))
        sep = '' if first else ','

        projected = (
                current_size
                + len(sep.encode('utf-8'))
                + len(item_str.encode('utf-8'))
                + len(']'.encode('utf-8'))
        )
        if not first and projected > max_size_bytes:
            out_path = open_new_chunk()
            sep = ''

        f_out.write(sep + item_str)
        current_size += len(sep.encode('utf-8')) + len(item_str.encode('utf-8'))
        first = False

    f_out.write(']')
    f_out.close()
    print(f"Wrote {out_path} ({os.path.getsize(out_path)} bytes)")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Stream-split a JSON array under "results" into chunks ≤ max size.'
    )
    parser.add_argument('input', help='Input JSON file with top-level "results" array')
    parser.add_argument('output_dir', help='Directory to write chunk files into')
    parser.add_argument(
        '--prefix', default='chunk',
        help='Filename prefix (default "chunk")'
    )
    parser.add_argument(
        '--max-size', type=int, default=40 * 1024 * 1024,
        help='Max bytes per chunk (default 40 MB)'
    )
    args = parser.parse_args()
    split_json_array(args.input, args.output_dir, args.prefix, args.max_size)
