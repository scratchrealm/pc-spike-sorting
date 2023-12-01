import os

def main():
    import MEArec as mr

    home_dir = os.path.expanduser('~')
    cell_models_folder = f'{home_dir}/.config/mearec/1.9.0/cell_models/bbp'

    tempgen = mr.gen_templates(
        cell_models_folder=cell_models_folder,
        params=None,
        templates_tmp_folder=None,
        intraonly=False,
        parallel=True,
        recompile=False,
        n_jobs=None,
        delete_tmp=True,
        verbose=True
    )

    mr.save_template_generator(tempgen, 'test1.templates.h5')

    print(tempgen)
if __name__ == '__main__':
    main()
