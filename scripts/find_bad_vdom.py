import os, glob

for p in glob.glob('ui/**/*.py', recursive=True):
    with open(p, encoding='utf-8') as f:
        for num, line in enumerate(f, 1):
            if 'html.' in line and '{"class' in line:
                parts = line.split('html.')
                for part in parts[1:]:
                    tag_and_args = part.split('(', 1)
                    if len(tag_and_args) > 1:
                        args = tag_and_args[1].strip()
                        if args and not args.startswith('{'):
                            print(f"{p}:{num}: {line.strip()}")
