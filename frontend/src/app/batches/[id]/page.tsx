import BatchDetailClient from "./BatchDetailClient";

export function generateStaticParams() {
  return [{ id: "_" }];
}

export default function BatchDetailPage() {
  return <BatchDetailClient />;
}
