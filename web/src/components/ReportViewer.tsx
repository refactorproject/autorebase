type Props = { src: string };
export default function ReportViewer({ src }: Props) {
  return (
    <iframe src={src} className="w-full h-[80vh] border" />
  );
}

