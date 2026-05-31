from app.schemas.pr import PullRequestData
from app.schemas.review import RuleFinding


SENSITIVE_PATH_KEYWORDS = {
    "auth": "认证/鉴权相关文件发生变更",
    "login": "登录流程相关文件发生变更",
    "permission": "权限控制相关文件发生变更",
    "role": "角色或权限模型相关文件发生变更",
    "token": "Token 处理相关文件发生变更",
    "payment": "支付相关文件发生变更",
    "billing": "计费相关文件发生变更",
    "sql": "数据库访问相关文件发生变更",
    "migration": "数据库迁移相关文件发生变更",
}

DANGEROUS_PATCH_PATTERNS = {
    "password": "代码变更中出现 password 字段，需要确认没有硬编码敏感信息",
    "secret": "代码变更中出现 secret 字段，需要确认没有泄露密钥",
    "api_key": "代码变更中出现 api_key 字段，需要确认没有泄露密钥",
    "eval(": "出现 eval 调用，可能带来代码执行风险",
    "verify=false": "关闭证书校验可能带来中间人攻击风险",
    "except pass": "异常被直接吞掉，可能掩盖线上问题",
}


def analyze_rules(pr: PullRequestData) -> list[RuleFinding]:
    findings: list[RuleFinding] = []

    for file in pr.changed_files:
        path = file.filename.lower()
        patch = file.patch.lower()

        for keyword, reason in SENSITIVE_PATH_KEYWORDS.items():
            if keyword in path:
                findings.append(
                    RuleFinding(
                        file=file.filename,
                        severity="medium",
                        title="敏感模块变更",
                        reason=reason,
                    )
                )
                break

        for pattern, reason in DANGEROUS_PATCH_PATTERNS.items():
            if pattern in patch:
                findings.append(
                    RuleFinding(
                        file=file.filename,
                        severity="high",
                        title="疑似高风险代码模式",
                        reason=reason,
                    )
                )

        if file.deletions > 100 and file.additions < 20:
            findings.append(
                RuleFinding(
                    file=file.filename,
                    severity="medium",
                    title="大段代码删除",
                    reason="该文件删除较多代码，需要确认没有移除必要校验或测试覆盖。",
                )
            )

        if "test" in path and file.deletions > file.additions:
            findings.append(
                RuleFinding(
                    file=file.filename,
                    severity="medium",
                    title="测试覆盖减少",
                    reason="测试文件删除多于新增，需要确认核心行为仍被覆盖。",
                )
            )

    return findings

