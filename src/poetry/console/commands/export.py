from cleo.helpers import option

from poetry.console.commands.command import Command
from poetry.utils.exporter import Exporter


class ExportCommand(Command):

    name = "export"
    description = "Exports the lock file to alternative formats."

    options = [
        option(
            "format",
            "f",
            "Format to export to. Currently, only requirements.txt is supported.",
            flag=False,
            default=Exporter.FORMAT_REQUIREMENTS_TXT,
        ),
        option("output", "o", "The name of the output file.", flag=False),
        option("without-hashes", None, "Exclude hashes from the exported file."),
        option(
            "without-urls",
            None,
            "Exclude source repository urls from the exported file.",
        ),
        option("dev", None, "Include development dependencies."),
        option(
            "extras",
            "E",
            "Extra sets of dependencies to include.",
            flag=False,
            multiple=True,
        ),
        option("with-credentials", None, "Include credentials for extra indices."),
    ]

    def handle(self) -> None:
        fmt = self.option("format")

        if fmt not in Exporter.ACCEPTED_FORMATS:
            raise ValueError(f"Invalid export format: {fmt}")

        output = self.option("output")

        locker = self.poetry.locker
        if not locker.is_locked():
            self.line_error("<comment>The lock file does not exist. Locking.</comment>")
            options = []
            if self.io.is_debug():
                options.append("-vvv")
            elif self.io.is_very_verbose():
                options.append("-vv")
            elif self.io.is_verbose():
                options.append("-v")

            self.call("lock", " ".join(options))

        if not locker.is_fresh():
            self.line_error(
                "<warning>"
                "Warning: The lock file is not up to date with "
                "the latest changes in pyproject.toml. "
                "You may be getting outdated dependencies. "
                "Run update to update them."
                "</warning>"
            )

        exporter = Exporter(self.poetry)
        exporter.export(
            fmt,
            self.poetry.file.parent,
            output or self.io,
            with_hashes=not self.option("without-hashes"),
            dev=self.option("dev"),
            extras=self.option("extras"),
            with_credentials=self.option("with-credentials"),
            with_urls=not self.option("without-urls"),
        )
