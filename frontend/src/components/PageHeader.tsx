import { CopyOutlined } from "@ant-design/icons";
import { Button, message } from "antd";
import type { ReactNode } from "react";

interface Props {
  title: string;
  extra?: ReactNode;
  children: ReactNode;
}

export default function PageHeader({ title, extra, children }: Props) {
  return (
    <div className="page-title">
      <div>
        <h2>{title}</h2>
        <div className="desc">{children}</div>
      </div>
      {extra}
    </div>
  );
}

export function CopyButton({ text }: { text: string }) {
  return (
    <Button
      size="small"
      icon={<CopyOutlined />}
      onClick={async () => {
        await navigator.clipboard.writeText(text);
        message.success("已复制");
      }}
    >
      复制文案
    </Button>
  );
}
