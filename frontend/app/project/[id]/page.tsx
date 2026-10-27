// frontend/app/project/[id]/page.tsx

export default async function ProjectPage(props: any{
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <div>
      {/* Your existing Project page component code here */}
    </div>
  );
}