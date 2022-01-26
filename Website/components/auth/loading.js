import Layout from "../layout/layout";
import Title from "../content/title";
import {ImSpinner2} from "react-icons/im";
import React from "react";

export default function Loading() {
    return (
        <Layout>
            <Title>
                <div className="flex flex-row items-end gap-4">
                    Loading
                    <ImSpinner2 className="animate-spin"/>
                </div>
            </Title>
        </Layout>
    )
}
