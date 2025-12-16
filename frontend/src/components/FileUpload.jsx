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
    reset,
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
    if (e.dataTransfer.types.includes("Files")) {
      setIsDragging(true);
    }
  };
  const handleFormDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
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
        "space-y-8 rounded-2xl border-2 transition-all duration-200", 
        "glass-strong shadow-glassxl p-8 w-full",
        isDragging ? "border-accent-vibrant bg-accent-vibrant/10" : "border-dark-700"
      )}
      onDragOver={handleFormDragOver}
      onDragLeave={handleFormDragLeave}
      onDrop={handleFormDrop}
    >
      <div className="flex flex-col items-center justify-center gap-4 text-center">
        <div className="flex h-20 w-20 items-center justify-center rounded-full bg-accent-vibrant/15 text-accent-vibrant shadow-glass">
          <CloudArrowUpIcon className="h-10 w-10" />
        </div>
        <div>
          <h2 className="text-2xl font-bold leading-tight mb-2 tracking-tight bg-gradient-to-br from-primary-300 via-accent-vibrant to-accent-purple bg-clip-text text-transparent ">
            Upload Resume
          </h2>
          <p className="max-w-md text-sm text-slate-300">
            Drop a PDF or DOCX resume here. Optionally provide a job description so we can tailor the AI scoring.
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
            if (!file) return "Resume file is required";
            if (file.size > 10 * 1024 * 1024) return "File must be smaller than 10MB";
            return true;
          },
        }}
        render={({ field: { onChange, value, ...field } }) => {
          const handleDragOver = (e) => { e.preventDefault(); e.stopPropagation(); setIsDragging(true); };
          const handleDragLeave = (e) => { e.preventDefault(); e.stopPropagation(); setIsDragging(false); };
          const handleDrop = (e) => {
            e.preventDefault(); e.stopPropagation(); setIsDragging(false);
            const files = e.dataTransfer.files;
            if (files && files.length > 0) {
              const file = files[0];
              const validTypes = [".pdf", ".doc", ".docx"];
              const ext = "." + file.name.split(".").pop().toLowerCase();
              if (!validTypes.includes(ext)) return;
              const dt = new DataTransfer(); dt.items.add(file);
              setFileName(file.name); onChange(dt.files);
            }
          };
          const handleFileInputChange = (event) => {
            const files = event.target.files; if (files && files.length > 0) {
              setFileName(files[0].name); onChange(files);
            } else { setFileName(""); onChange(null); }
          };
          return (
            <div
              className={clsx(
                "mt-5 mb-2 rounded-xl border-2 border-dashed flex flex-col items-center justify-center p-8 bg-glass/60 backdrop-blur transition-all duration-200",
                isDragging ? "border-accent-vibrant bg-accent-vibrant/10" : errors.resume ? "border-red-400 bg-red-900/40" : "border-dark-700 bg-dark-900/60"
              )}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <label htmlFor="resume" className="flex cursor-pointer flex-col items-center justify-center gap-2 text-sm text-slate-200 select-none">
                <span className="rounded-full bg-slate-100/5 px-4 py-1 text-xs font-semibold text-accent-vibrant shadow-sm">
                  Choose resume file
                </span>
                <input {...field} id="resume" type="file" accept=".pdf,.doc,.docx" className="hidden" onChange={handleFileInputChange} />
                <span className="text-accent-vibrant text-xs mt-2 font-semibold select-none">
                  {fileName || "Drag & drop to upload, or click to browse"}
                </span>
              </label>
              {errors.resume && (
                <p className="mt-2 text-xs text-red-400 font-bold animate-bounce">{errors.resume.message}</p>
              )}
            </div>
          );
        }}
      />

      <div className="grid gap-6 md:grid-cols-2">
        <div className="space-y-2">
          <label className="block text-xs font-semibold text-slate-400 uppercase" htmlFor="candidate_name">Candidate Name</label>
          <input id="candidate_name" placeholder="Jane Doe" className="w-full rounded-xl border border-dark-700 bg-glass/60 px-4 py-2 text-sm text-slate-200 shadow-sm focus:border-accent-vibrant focus:ring-2 focus:ring-accent-vibrant transition" {...register("candidate_name")} />
        </div>
        <div className="space-y-2">
          <label className="block text-xs font-semibold text-slate-400 uppercase" htmlFor="background">Notes (optional)</label>
          <input id="background" placeholder="Internal referral, frontend focus, etc." className="w-full rounded-xl border border-dark-700 bg-glass/60 px-4 py-2 text-sm text-slate-200 shadow-sm focus:border-accent-purple focus:ring-2 focus:ring-accent-purple transition" {...register("background")} />
        </div>
      </div>
      <div className="space-y-2">
        <label className="block text-xs font-semibold text-slate-400 uppercase" htmlFor="job_description">Job Description</label>
        <textarea id="job_description" rows={6} placeholder="Paste the role summary or job requirements here..." className="w-full rounded-xl border border-dark-700 bg-glass/60 px-4 py-3 text-sm text-slate-200 shadow-sm focus:border-accent-vibrant focus:ring-2 focus:ring-accent-vibrant transition" {...register("job_description")} />
        <p className="text-xs text-slate-500">Adding a job description enables semantic matching using transformer embeddings.</p>
      </div>
      <button type="submit" disabled={isSubmitting} className="mt-4 w-full rounded-xl bg-gradient-to-br from-accent-vibrant via-primary-600 to-accent-purple px-6 py-3 text-base font-bold uppercase tracking-wider text-white shadow-xl hover:scale-[1.02] hover:shadow-glassxl focus:outline-none focus:ring-2 focus:ring-accent-vibrant transition-all duration-150 disabled:opacity-70">
        {isSubmitting ? "Analyzing..." : "Run AI Screening"}
      </button>
    </form>
  );
}

export default FileUpload;

