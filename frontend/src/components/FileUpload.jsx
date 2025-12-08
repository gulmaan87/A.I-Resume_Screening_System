import { useForm, Controller } from "react-hook-form";
import { useState } from "react";
import { CloudArrowUpIcon } from "@heroicons/react/24/solid";
import clsx from "clsx";

function FileUpload({ onSubmit, isSubmitting }) {
  const {
    control,
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm();
  const [fileName, setFileName] = useState("");
  const [isDragging, setIsDragging] = useState(false);

  const submitHandler = (values) => {
    onSubmit(values, () => {
      reset();
      setFileName("");
    });
  };

  const handleFormDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.types.includes('Files')) {
      setIsDragging(true);
    }
  };

  const handleFormDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    // Only set dragging to false if we're leaving the form area
    if (!e.currentTarget.contains(e.relatedTarget)) {
      setIsDragging(false);
    }
  };

  const handleFormDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  return (
    <form
      onSubmit={handleSubmit(submitHandler)}
      className={clsx(
        "space-y-6 rounded-xl border-2 border-dashed bg-white p-8 shadow-sm transition-all",
        isDragging ? "border-primary-400 bg-primary-50" : "border-primary-200"
      )}
      onDragOver={handleFormDragOver}
      onDragLeave={handleFormDragLeave}
      onDrop={handleFormDrop}
    >
      <div className="flex flex-col items-center justify-center gap-4 text-center">
        <div className="flex h-20 w-20 items-center justify-center rounded-full bg-primary-50 text-primary-600">
          <CloudArrowUpIcon className="h-10 w-10" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-slate-800">Upload Resume</h2>
          <p className="max-w-md text-sm text-slate-500">
            Drop a PDF or DOCX resume here. Optionally provide a job description so we can tailor the
            AI scoring.
          </p>
        </div>
      </div>

      <Controller
        name="resume"
        control={control}
        rules={{
          required: "Resume file is required",
          validate: (value) => {
            if (!value || value.length === 0) {
              return "Resume file is required";
            }
            const file = value[0];
            if (!file) {
              return "Resume file is required";
            }
            if (file.size > 10 * 1024 * 1024) {
              return "File must be smaller than 10MB";
            }
            return true;
          }
        }}
        render={({ field: { onChange, value, ...field } }) => {
          const handleDragOver = (e) => {
            e.preventDefault();
            e.stopPropagation();
            setIsDragging(true);
          };

          const handleDragLeave = (e) => {
            e.preventDefault();
            e.stopPropagation();
            setIsDragging(false);
          };

          const handleDrop = (e) => {
            e.preventDefault();
            e.stopPropagation();
            setIsDragging(false);

            const files = e.dataTransfer.files;
            if (files && files.length > 0) {
              const file = files[0];
              // Validate file type
              const validTypes = ['.pdf', '.doc', '.docx'];
              const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
              
              if (!validTypes.includes(fileExtension)) {
                return; // Invalid file type, don't set
              }

              // Create a FileList-like object
              const dataTransfer = new DataTransfer();
              dataTransfer.items.add(file);
              
              setFileName(file.name);
              onChange(dataTransfer.files);
            }
          };

          const handleFileInputChange = (event) => {
            const files = event.target.files;
            if (files && files.length > 0) {
              const file = files[0];
              setFileName(file.name);
              onChange(files);
            } else {
              setFileName("");
              onChange(null);
            }
          };

          return (
            <div
              className={clsx(
                "rounded-lg border-2 border-dashed p-6 transition-all",
                isDragging
                  ? "border-primary-400 bg-primary-50"
                  : errors.resume
                  ? "border-red-400 bg-red-50"
                  : "border-slate-200 bg-slate-50"
              )}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <label
                htmlFor="resume"
                className="flex cursor-pointer flex-col items-center justify-center gap-2 text-sm text-slate-600"
              >
                <span className="rounded-full bg-white px-4 py-1 text-xs font-semibold text-primary-600 shadow-sm">
                  Choose resume file
                </span>
                <input
                  {...field}
                  id="resume"
                  type="file"
                  accept=".pdf,.doc,.docx"
                  className="hidden"
                  onChange={handleFileInputChange}
                />
                <span className="text-slate-500">
                  {fileName || "Drag & drop to upload, or click to browse"}
                </span>
              </label>
              {errors.resume && <p className="mt-2 text-sm text-red-500">{errors.resume.message}</p>}
            </div>
          );
        }}
      />

      <div className="grid gap-5 md:grid-cols-2">
        <div className="space-y-2">
          <label className="block text-sm font-semibold text-slate-700" htmlFor="candidate_name">
            Candidate Name
          </label>
          <input
            id="candidate_name"
            placeholder="Jane Doe"
            className="w-full rounded-lg border border-slate-200 px-4 py-2 text-sm shadow-sm focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-100"
            {...register("candidate_name")}
          />
        </div>
        <div className="space-y-2">
          <label className="block text-sm font-semibold text-slate-700" htmlFor="background">
            Notes (optional)
          </label>
          <input
            id="background"
            placeholder="Internal referral, frontend focus, etc."
            className="w-full rounded-lg border border-slate-200 px-4 py-2 text-sm shadow-sm focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-100"
            {...register("background")}
          />
        </div>
      </div>

      <div className="space-y-2">
        <label className="block text-sm font-semibold text-slate-700" htmlFor="job_description">
          Job Description
        </label>
        <textarea
          id="job_description"
          rows={6}
          placeholder="Paste the role summary or job requirements here..."
          className="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm shadow-sm focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-100"
          {...register("job_description")}
        />
        <p className="text-xs text-slate-500">
          Adding a job description enables semantic matching using transformer embeddings.
        </p>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-primary-700 disabled:cursor-not-allowed disabled:bg-primary-400"
      >
        {isSubmitting ? "Analyzing..." : "Run AI Screening"}
      </button>
    </form>
  );
}

export default FileUpload;

