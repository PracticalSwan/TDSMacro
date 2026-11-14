"""Copy installed dependency and Python notices into an already built app."""
import importlib.metadata
import shutil
import sys
from pathlib import Path


def collect(app):
    target=Path(app)/'THIRD_PARTY_LICENSES'
    target.mkdir(parents=True,exist_ok=True)
    count=0
    for dist in importlib.metadata.distributions():
        for entry in dist.files or ():
            if not entry.name.casefold().startswith(('license','copying','notice')):
                continue
            source=Path(dist.locate_file(entry))
            if not source.is_file():
                continue
            destination=target/dist.metadata['Name']/Path(*entry.parts)
            if not destination.resolve().is_relative_to(target.resolve()):
                raise ValueError('Dependency notice escaped output directory.')
            destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,destination)
            count+=1
    python_license=Path(sys.base_prefix)/'LICENSE.txt'
    if not python_license.is_file():
        raise FileNotFoundError('Python license missing; inspect installation before release.')
    shutil.copyfile(python_license,target/'Python-LICENSE.txt')
    print(f'Collected {count+1} dependency/Python notices.')


if __name__=='__main__':
    collect(sys.argv[1])
