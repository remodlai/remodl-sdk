from typing import Optional

from remodl.types.llms.openai import CreateFileRequest
from remodl.types.utils import ExtractedFileData


class FilesAPIUtils:
    """
    Utils for files API interface on remodl
    """
    @staticmethod
    def is_batch_jsonl_file(create_file_data: CreateFileRequest, extracted_file_data: ExtractedFileData) -> bool:
        """
        Check if the file is a batch jsonl file
        """
        return (
            create_file_data.get("purpose") == "batch"
            and FilesAPIUtils.valid_content_type(extracted_file_data.get("content_type"))
            and extracted_file_data.get("content") is not None
        )
    
    @staticmethod
    def valid_content_type(content_type: Optional[str]) -> bool:
        """
        Check if the content type is valid
        """
        return content_type in set(["application/jsonl", "application/octet-stream"])
